"""
WordsProject-forstudent - 单词清洗与匹配模块

功能：
1. 检查/创建输出目录
2. 遍历输入目录中的所有文件
3. 只处理.txt文件
4. 对每个文件：
   a. 读取内容
   b. 用正则表达式删除中文 即提取所有单词
   c. 去重(set)并排序(sort)
   d. 写入新文件(每个单词一行)

Copyright (c) 2024 WordsProject-forstudent Authors
"""

import re
import os
import sys
from datetime import datetime
from pathlib import Path

# 将项目根目录加入 sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import json
import random

# enchant 在 Windows 上可能需要额外安装词典
enchant_dict = None
try:
    import enchant
    enchant_dict = enchant.Dict("en_US")
except Exception:  # 捕获 DictNotFoundError 或其他异常
    print("警告: enchant 词典未安装，拼写检查功能将不可用")

from scripts.config import Config


def get_latest(file_path: str) -> str | None:
    """
    获取指定目录中最新的txt文件。

    Args:
        file_path: 目录路径

    Returns:
        最新文件的名称，如果目录为空则返回None
    """
    red_all = os.scandir(file_path)

    latest_list = max(
        (entry for entry in red_all if entry.is_file()),
        key=lambda x: x.stat().st_mtime,
        default=None
    )
    print(file_path, "读取到最新文件...")
    try:
        if latest_list and latest_list.name.endswith(".txt"):
            print(f"读取成功！文件名：{latest_list.name}")
    except AttributeError as e:
        print(f"读取失败！{e}")
        return None

    return latest_list.name if latest_list else None


def get_latest_with_date(base_name: str, path: str) -> tuple[str, str]:
    """
    生成带日期的文件名。

    Args:
        base_name: 文件基础名
        path: 文件目录路径

    Returns:
        tuple[文件名, 完整路径]
    """
    date_str = datetime.now().strftime("%Y%m%d")
    new_filename = f"{base_name}_{date_str}.txt"
    new_filepath = os.path.join(path, new_filename)

    count = 1
    while os.path.exists(new_filepath):
        new_filename = f"{base_name}_{date_str}_{count}.txt"
        new_filepath = os.path.join(path, new_filename)
        count += 1

    return new_filename, new_filepath


def delete_chinese(file_path: str | None = None) -> str:
    """
    清洗导入的单词表，提取英文单词。

    Args:
        file_path: 可选，指定文件路径

    Returns:
        清洗后文件的完整路径
    """
    print("检查文件中...")
    print("读取最新中...")
    config = Config()
    custom_path = config.CUSTOM
    latest_list = get_latest(str(custom_path))

    if not latest_list:
        raise FileNotFoundError(f"未找到任何txt文件于 {custom_path}")

    print("开始清洗中...")
    cleaned_lines = []
    eng_dict = enchant_dict

    with open(os.path.join(custom_path, latest_list), 'r', encoding='utf-8') as f:
        all_lines = f.readlines()

    total_lines = len(all_lines)
    print(f"总共需要处理 {total_lines} 行数据")

    for i, line in enumerate(all_lines):
        if i % 100 == 0:
            print(f"正在处理第 {i}/{total_lines} 行...")

        match = re.match(r'^\d+\.([a-zA-Z\s\.\'-]+)\s*[-;]', line)
        if match:
            cleaned = match.group(1).strip()
            if re.search(r'\d', cleaned):
                continue
            if eng_dict is None or all(eng_dict.check(word) for word in cleaned.split()):
                cleaned_lines.append(cleaned)
            else:
                print(f"无法识别的单词: {cleaned}，请检查一遍后再补充导入。")
        elif line.strip() and not line.startswith(';'):
            cleaned_lines.append(line.split()[0])

    date_str = datetime.now().strftime("%Y%m%d")
    new_filename = f"new_lists_{date_str}.txt"
    after_path = os.path.join(custom_path, "after")
    new_filepath = os.path.join(after_path, new_filename)

    counter = 1
    while os.path.exists(new_filepath):
        new_filename = f"new_lists_{date_str}_{counter}.txt"
        new_filepath = os.path.join(after_path, new_filename)
        counter += 1

    unique_words = sorted(
        set(word.strip() for word in cleaned_lines),
        key=lambda x: x.lower()
    )

    os.makedirs(after_path, exist_ok=True)

    with open(new_filepath, 'w', encoding='utf-8') as f:
        for word in unique_words:
            f.write(word + '\n')

    print(f"清洗完成！结果已保存至 {new_filepath}")
    print(f"共处理了 {len(unique_words)} 个有效单词")
    match_and_save(new_filename)
    return new_filepath


def load_corpus() -> dict[str, list[dict[str, str]]]:
    """
    加载CC-CEDICT语料库文件，构建反向索引。

    Returns:
        反向索引字典 {英文释义: [{simplified: 中文释义}, ...]}
    """
    print("加载语料库中...")
    config = Config()
    reverse_index = {}
    cedict_path = os.path.join(config.DATA_DIR, "cedict_ts.u8.txt")

    with open(cedict_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.split('/')
            chinese_info = parts[0].strip().split()
            simplified = chinese_info[1]
            english_meanings = parts[1:-1]

            for meaning in english_meanings:
                if meaning:
                    existing = next(
                        (item for item in reverse_index.get(meaning, [])
                         if 'simplified' in item),
                        None
                    )
                    if existing:
                        existing['simplified'] += f";{simplified}"
                    else:
                        reverse_index.setdefault(meaning, []).append({
                            'simplified': simplified
                        })

    return reverse_index


def match_and_save(latest_file: str | None) -> None:
    """
    读取单词列表并与CC-CEDICT语料库进行匹配。

    Args:
        latest_file: 最新单词文件名
    """
    print("匹配单词汉释中...")
    reverse_index = load_corpus()

    if not latest_file:
        print("未找到最新单词表，无法进行匹配。")
        return

    config = Config()
    words = []
    count = 0
    after_path = os.path.join(config.CUSTOM, "after")

    with open(os.path.join(after_path, latest_file), 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip()
            count += 1
            words.append(word)

    print(f"读取到{count}个单词")

    result = {}
    for word in words:
        result[word] = reverse_index.get(word, [])

    merged_result = {}
    matched_files = [f for f in os.listdir(config.MATCHED) if f.endswith('.json')]

    for file_name in matched_files:
        file_path = os.path.join(config.MATCHED, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                merged_result.update(existing_data)
        except Exception as e:
            print(f"读取文件 {file_name} 时出错: {e}")

    merged_result.update(result)

    filtered = {
        k: v
        for k, v in merged_result.items()
        if not (isinstance(v, list) and len(v) == 0)
    }

    for file_name in matched_files:
        file_path = os.path.join(config.MATCHED, file_name)
        os.remove(file_path)

    new_filename = "merged_word_list.json"
    new_filepath = os.path.join(config.MATCHED, new_filename)
    os.makedirs(config.MATCHED, exist_ok=True)

    with open(new_filepath, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=4)

    print(f"匹配结果已合并保存至 {new_filepath}")


def check_unmatched_words() -> None:
    """
    检查matched文件夹中的JSON文件，提取没有simplified键的单词到un_matched文件夹。
    """
    print("检查未匹配的单词...")
    config = Config()
    os.makedirs(config.UN_MATCHED, exist_ok=True)

    matched_file = os.path.join(config.MATCHED, "merged_word_list.json")

    if not os.path.exists(matched_file):
        print("未找到匹配文件，无需检查未匹配单词。")
        return

    with open(matched_file, 'r', encoding='utf-8') as f:
        matched_data = json.load(f)

    unmatched_words = []
    for word, definitions in list(matched_data.items()):
        if not definitions or not any('simplified' in definition for definition in definitions):
            unmatched_words.append(word)
            del matched_data[word]

    if unmatched_words:
        date_str = datetime.now().strftime("%Y%m%d")
        unmatched_filename = f"unmatched_words_{date_str}.txt"
        unmatched_filepath = os.path.join(config.UN_MATCHED, unmatched_filename)

        counter = 1
        while os.path.exists(unmatched_filepath):
            unmatched_filename = f"unmatched_words_{date_str}_{counter}.txt"
            unmatched_filepath = os.path.join(config.UN_MATCHED, unmatched_filename)
            counter += 1

        with open(unmatched_filepath, 'w', encoding='utf-8') as f:
            for word in unmatched_words:
                f.write(word + '\n')

        print(f"找到 {len(unmatched_words)} 个未匹配的单词，已保存至 {unmatched_filepath}")

        with open(matched_file, 'w', encoding='utf-8') as f:
            json.dump(matched_data, f, ensure_ascii=False, indent=2)
        print(f"已从匹配文件中删除未匹配的单词，剩余 {len(matched_data)} 个已匹配单词")
    else:
        print("所有单词都已成功匹配！")


if __name__ == "__main__":
    un_matched = delete_chinese()
    check_unmatched_words()
