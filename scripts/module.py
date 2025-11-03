import os
from datetime import datetime
import requests
import json
from tqdm import tqdm
import random

from .config import Config

from scripts.clean_words import delete_chinese,get_latest,check_unmatched_words,match_and_save

def random_word(words_with_chinese):
    random_words = []
    count = 0
    while count < 10:
        ran_word_w_chinese = random.choice(words_with_chinese) # 随机选择单词 每次一个
        # print("测试 ",ran_word_w_chinese)
        # print("单词：",ran_word_w_chinese['english'])

        # 检查是否已存在该单词
        flag = any(word['english'] == ran_word_w_chinese['english'] for word in random_words)

        if not flag:
            random_words.append(ran_word_w_chinese)
            count += 1
            return random_words
        else:
            print(ran_word_w_chinese['english'], "单词重复")

def cedict_download():
    config = Config()
    url = "https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz"
    response = requests.get(url, stream=True)
    response.raise_for_status()  # 检查请求是否成功
    total_size = int(response.headers.get('content-length', 0))# 下载文件并显示进度条
    with open(config.CEDICT,"wb") as f,tqdm(
        desc = config.CEDICT,total=total_size,unit="B",unit_scale=True
    ) as bar:
        for data in response.iter_content(chunk_size=8192): # chunk_size 每次读取的字节数
            size = f.write(data)
            bar.update(size)

def get_random_questions(num_questions):
    config = Config()
    # 从matched文件夹读取JSON文件
    custom_file = get_latest(config.CUSTOM)
    delete_chinese(custom_file)
    matched_json_path = config.DATA_DIR / "word_lists" / "matched" / "merged_word_list.json"
    print(matched_json_path)

    with open(matched_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 数据有效性过滤
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
    for _ in range(min(num_questions, len(valid_keys))):  # 防越界
            q_key = random.choice(valid_keys)
            correct = data[q_key][0]["simplified"]


        # 干扰项
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

def get_cet4_random_questions(num_questions):
    # 从matched文件夹读取JSON文件
    matched_json_path = "data/word_lists/local/cet4.json"

    with open(matched_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_keys = list(data.keys())
    questions = []

    for _ in range(num_questions):
        q_key = random.choice(all_keys)
        correct = data[q_key][0]["simplified"]

        # 干扰项
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

def get_cet6_random_questions(num_questions):
    config = Config()
    # 从matched文件夹读取JSON文件
    matched_json_path = config.CET / "cet6.json"
    
    with open(matched_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_keys = list(data.keys())
    questions = []

    for _ in range(num_questions):
        q_key = random.choice(all_keys)
        correct = data[q_key][0]["simplified"]

        # 干扰项
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