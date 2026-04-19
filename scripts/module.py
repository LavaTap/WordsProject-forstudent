"""
WordsProject-forstudent - 题目模块

功能：
1. 下载CC-CEDICT语料库
2. 随机生成词汇测验题目
3. 支持自定义、四级、六级模式

Copyright (c) 2024 WordsProject-forstudent Authors
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# 将项目根目录加入 sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import requests
import json
from tqdm import tqdm
import random

from scripts.config import Config
from scripts.clean_words import delete_chinese, get_latest, check_unmatched_words, match_and_save


def random_word(words_with_chinese: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    从单词列表中随机选择单词。

    Args:
        words_with_chinese: 包含中文释义的单词列表

    Returns:
        随机选择的单词列表（最多10个不重复）
    """
    random_words = []
    count = 0
    while count < 10:
        ran_word_w_chinese = random.choice(words_with_chinese)
        flag = any(word['english'] == ran_word_w_chinese['english'] for word in random_words)

        if not flag:
            random_words.append(ran_word_w_chinese)
            count += 1
            return random_words
        else:
            print(ran_word_w_chinese['english'], "单词重复")


def cedict_download() -> None:
    """
    下载CC-CEDICT语料库文件。
    """
    config = Config()
    url = "https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz"
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get('content-length', 0))

    with open(config.CEDICT, "wb") as f, tqdm(
        desc=str(config.CEDICT),
        total=total_size,
        unit="B",
        unit_scale=True
    ) as bar:
        for data in response.iter_content(chunk_size=8192):
            size = f.write(data)
            bar.update(size)


def get_random_questions(num_questions: int) -> list[dict[str, Any]]:
    """
    获取随机测验题目（自定义模式）。

    Args:
        num_questions: 题目数量

    Returns:
        题目列表，每题包含 question、options、answer
    """
    config = Config()
    custom_file = get_latest(str(config.CUSTOM))
    delete_chinese(custom_file)
    matched_json_path = config.DATA_DIR / "word_lists" / "matched" / "merged_word_list.json"
    print(matched_json_path)

    with open(matched_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    valid_keys = [
        k for k in data.keys()
        if data[k] and isinstance(data[k], list)
        and len(data[k]) > 0
        and "simplified" in data[k][0]
    ]
    if not valid_keys:
        return [{"error": "No valid question data available"}]

    all_keys = list(data.keys())
    questions = []

    for _ in range(min(num_questions, len(valid_keys))):
        q_key = random.choice(valid_keys)
        correct = data[q_key][0]["simplified"]

        distractors = []
        while len(distractors) < 3:
            dk = random.choice(all_keys)
            if dk != q_key:
                distractor = data[dk][0]["simplified"]
                if distractor not in distractors:
                    distractors.append(distractor)

        options = distractors + [correct]
        random.shuffle(options)

        questions.append({
            "question": q_key,
            "options": options,
            "answer": correct
        })

    return questions


def get_cet4_random_questions(num_questions: int) -> list[dict[str, Any]]:
    """
    获取随机测验题目（CET-4模式）。

    Args:
        num_questions: 题目数量

    Returns:
        题目列表
    """
    config = Config()
    matched_json_path = config.CET / "cet4.json"

    with open(matched_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_keys = list(data.keys())
    questions = []

    for _ in range(num_questions):
        q_key = random.choice(all_keys)
        correct = data[q_key][0]["simplified"]

        distractors = []
        while len(distractors) < 3:
            dk = random.choice(all_keys)
            if dk != q_key:
                distractor = data[dk][0]["simplified"]
                if distractor not in distractors:
                    distractors.append(distractor)

        options = distractors + [correct]
        random.shuffle(options)

        questions.append({
            "question": q_key,
            "options": options,
            "answer": correct
        })

    return questions


def get_cet6_random_questions(num_questions: int) -> list[dict[str, Any]]:
    """
    获取随机测验题目（CET-6模式）。

    Args:
        num_questions: 题目数量

    Returns:
        题目列表
    """
    config = Config()
    matched_json_path = config.CET / "cet6.json"

    with open(matched_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_keys = list(data.keys())
    questions = []

    for _ in range(num_questions):
        q_key = random.choice(all_keys)
        correct = data[q_key][0]["simplified"]

        distractors = []
        while len(distractors) < 3:
            dk = random.choice(all_keys)
            if dk != q_key:
                distractor = data[dk][0]["simplified"]
                if distractor not in distractors:
                    distractors.append(distractor)

        options = distractors + [correct]
        random.shuffle(options)

        questions.append({
            "question": q_key,
            "options": options,
            "answer": correct
        })

    return questions
