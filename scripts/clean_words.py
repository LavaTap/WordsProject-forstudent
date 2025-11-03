import re # 正则表达式
import os
from datetime import datetime 

from .config import Config # 文件路径配置文件
import requests
import json
import random
from .config import Config
config = Config()
import enchant



script_name = os.path.basename(__file__)  # 获取当前脚本文件名
'''
clean_words.py

1. 检查/创建输出目录
2. 遍历输入目录中的所有文件
3. 只处理.txt文件
4. 对每个文件：
   a. 读取内容
   b. 用正则表达式删除中文 即提取所有单词
   c. 去重(set)并排序(sort)
   d. 写入新文件(每个单词一行)
'''


# 检查文件夹是否为空
# def check_files():
#     config = Config()
#     if not os.path.exists(config.CEDICT):
#         print(f"{config.CEDICT}路径未找到CC - CEDICT语料库文件,即将前往官网下载...")
#         cedict_download()
    
#     if os.path.getsize(config.WORD_LISTS) == 0:
#         print(f"{config.WORD_LISTS}单词表为空，请重新下载四六级词库，否则本地词库无法使用")

def get_latest(file_path):
    red_all = os.scandir(file_path) # 获取目录条目迭代器 此下的所有文件和文件夹

    latest_list = max ( # entry 进入
        (entry for entry in red_all if entry.is_file()), # 过滤出文件条目
        key = lambda x : x.stat().st_mtime, # 按文件修改时间排序
        default = None # 如果没有文件 返回None
    )
    print(file_path,"读取到最新文件...")
    try:
        if latest_list and latest_list.name.endswith(".txt"):
            print(f"读取成功！文件名：{latest_list.name}")
    except AttributeError as e: # 访问对象的属性时出现问题
        print(f"读取失败！{e}")
        return None

    return latest_list and latest_list.name # 返回最新文件的路径

def file_name(base_name,path):
    # 生成带日期的文件名
    date_str = datetime.now().strftime("%Y%m%d") # 格式化日期为字符串
    new_filename = f"{base_name}_{date_str}.txt"
    new_filepath = os.path.join([path])

    # 查重
    count = 1
    while os.path.exists(new_filepath):
        new_filename = f"{base_name}_{date_str}_{count}.txt"
        new_filepath = os.path.join([path])
        count += 1


# 自定义模式 清洗导入单词表
def delete_chinese(file_path):
    print("检查文件中...")
    print("读取最新中...")
    custom_path = config.CUSTOM
    latest_list = get_latest(custom_path)
    print("开始清洗中...")
    cleaned_lines = []  # 用于存储筛选后的单词列表
    eng_dict = enchant.Dict("en_US")  # 创建英语词典对象
    
    # 先读取所有行以计算总数
    with open(os.path.join(custom_path,latest_list), 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
    
    total_lines = len(all_lines)
    print(f"总共需要处理 {total_lines} 行数据")
    
    for i, line in enumerate(all_lines):
        # 显示进度
        if i % 100 == 0:
            print(f"正在处理第 {i}/{total_lines} 行...")
            
        match = re.match(r'^\d+\.([a-zA-Z\s\.\'-]+)\s*[-;]', line)
        if match:
            cleaned = match.group(1).strip()
            if re.search(r'\d', cleaned):
                continue
            # 使用PyEnchant验证
            if all(eng_dict.check(word) for word in cleaned.split()):
                cleaned_lines.append(cleaned)
            else:
                print(f"无法识别的单词: {cleaned}，请检查一遍后再补充导入。")
        elif line.strip() and not line.startswith(';'):
            # 处理没有分隔符但需要保留的行
            cleaned_lines.append(line.split()[0])

    # 生成带日期的新文件名
    date_str = datetime.now().strftime("%Y%m%d")
    new_filename = f"new_lists_{date_str}.txt"
    after_path = os.path.join(custom_path, "after")
    new_filepath = os.path.join(after_path, new_filename)

    # 检查文件是否存在，避免覆盖
    counter = 1
    while os.path.exists(new_filepath):
        new_filename = f"new_lists_{date_str}_{counter}.txt"
        new_filepath = os.path.join(after_path, new_filename)
        counter += 1

    unique_words = sorted(set(word.strip() for word in cleaned_lines), key=lambda x: x.lower())
    
    # 确保输出目录存在
    os.makedirs(after_path, exist_ok=True)
    
    # 保存到新文件
    with open(new_filepath, 'w', encoding='utf-8') as f:
        for word in unique_words:
            f.write(word + '\n')
    print(f"清洗完成！结果已保存至 {new_filepath}")
    print(f"共处理了 {len(unique_words)} 个有效单词")
    match_and_save(new_filename)
    return new_filepath

# from words_only import


'''
    从origin_lists读取最新文件 然后使用CC - CEDICT进行匹配 匹配到的单词存入matched中
    as f 是Python中的上下文管理器，用于确保文件在使用后正确关闭 f 是文件对象的名称
    scandir - 用于遍历目录中的文件和子目录
    split() - 分割字符串
    strip() - 去除字符串两端的空格
'''
# 读取CC - CEDICT语料库文件 构建反向索引 提高匹配效率

def load_corpus():
    print("加载语料库中...")
    config = Config()
    reverse_index = {}  # 构建反向索引
    cedict_path = os.path.join(config.DATA_DIR, "cedict_ts.u8.txt")
    with open(cedict_path, 'r', encoding='utf-8') as f:
        for line in f:
            # 跳过注释行
            if line.startswith('#'):
                continue
            # 解析词条信息
            parts = line.split('/')
            chinese_info = parts[0].strip().split()
            simplified = chinese_info[1]
            english_meanings = parts[1:-1]
            # 为每个英文释义建立反向索引
            for meaning in english_meanings:
                if meaning:
                    # 合并相同英文单词的所有中文释义
                    existing = next((item for item in reverse_index.get(meaning, []) if 'simplified' in item), None)
                    if existing:
                        existing['simplified'] += f";{simplified}"
                    else:
                        reverse_index.setdefault(meaning, []).append({
                            'simplified': simplified
                        })
    return reverse_index

# 读取最新的单词列表 并与CC - CEDICT语料库进行匹配 匹配到的单词存入new_lists中

def match_and_save(latest_file):
    print("匹配单词汉释中...")
    # 加载语料库并构建反向索引
    reverse_index = load_corpus()
    if not latest_file:
        print("未找到最新单词表，无法进行匹配。")
        return
    # 读取最新文件中的单词
    words = []
    count = 0
    after_path = os.path.join(config.CUSTOM, "after")
    with open(os.path.join(after_path, latest_file), 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip()
            count = count + 1
            words.append(word)
    print(f"读取到{count}个单词")
    # 匹配中文释义
    result = {}
    for word in words:
        result[word] = reverse_index.get(word, [])

    # 检查并合并现有matched文件夹中的文件
    merged_result = {}
    matched_files = [f for f in os.listdir(config.MATCHED) if f.endswith('.json')]

    
    # 读取并合并所有现有文件的内容
    for file_name in matched_files:
        file_path = os.path.join(config.MATCHED, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                merged_result.update(existing_data)
        except Exception as e:
            print(f"读取文件 {file_name} 时出错: {e}")
    
    # 合并新结果
    merged_result.update(result)

    # —— 在这里删除所有 value 为 [] 的键 —— 
    filtered = {
        k: v
        for k, v in merged_result.items()
        # 保留 v 非空 或者你需要的其他非空判断
        if not (isinstance(v, list) and len(v) == 0)
    }


    # 删除所有现有文件
    for file_name in matched_files:
        file_path = os.path.join(config.MATCHED, file_name)
        os.remove(file_path)

    # 保存为单个JSON文件
    new_filename = "merged_word_list.json"
    new_filepath = os.path.join(config.MATCHED, new_filename)

    # 确保输出目录存在
    os.makedirs(config.MATCHED, exist_ok=True)

    # 保存为 JSON 文件
    with open(new_filepath, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=4)
    print(f"匹配结果已合并保存至 {new_filepath}")



# 检查matched文件夹中的JSON文件，提取没有"simplified"键的单词到un_matched文件夹 最后删除未匹配成功的单词
def check_unmatched_words():
    print("检查未匹配的单词...")
    
    # 确保un_matched目录存在
    os.makedirs(config.UN_MATCHED, exist_ok=True)
    
    # 读取merged_word_list.json文件
    matched_file = os.path.join(config.MATCHED, "merged_word_list.json")
    
    if not os.path.exists(matched_file):
        print("未找到匹配文件，无需检查未匹配单词。")
        return
    
    # 读取匹配结果
    with open(matched_file, 'r', encoding='utf-8') as f:
        matched_data = json.load(f)
    
    # 提取没有"simplified"键的单词
    unmatched_words = []
    for word, definitions in list(matched_data.items()):
        if not definitions or not any('simplified' in definition for definition in definitions):
            unmatched_words.append(word)
            # 从原始数据中删除未匹配的单词
            del matched_data[word]
    
    # 如果有未匹配的单词，保存到un_matched文件夹
    if unmatched_words:
        date_str = datetime.now().strftime("%Y%m%d")
        unmatched_filename = f"unmatched_words_{date_str}.txt"
        unmatched_filepath = os.path.join(config.UN_MATCHED, unmatched_filename)
        
        # 检查文件是否存在，避免覆盖
        counter = 1
        while os.path.exists(unmatched_filepath):
            unmatched_filename = f"unmatched_words_{date_str}_{counter}.txt"
            unmatched_filepath = os.path.join(config.UN_MATCHED, unmatched_filename)
            counter += 1
        
        # 保存未匹配的单词
        with open(unmatched_filepath, 'w', encoding='utf-8') as f:
            for word in unmatched_words:
                f.write(word + '\n')
        
        print(f"找到 {len(unmatched_words)} 个未匹配的单词，已保存至 {unmatched_filepath}")
        
        # 更新原始JSON文件，删除未匹配的条目
        with open(matched_file, 'w', encoding='utf-8') as f:
            json.dump(matched_data, f, ensure_ascii=False, indent=2)
        print(f"已从匹配文件中删除未匹配的单词，剩余 {len(matched_data)} 个已匹配单词")
    else:
        print("所有单词都已成功匹配！")

if __name__ == "__main__":
    un_matched = delete_chinese()
    check_unmatched_words(un_matched)  # 添加检查未匹配单词的功能










