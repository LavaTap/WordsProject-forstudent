"""
WordsProject-forstudent - 数据库初始化模块

初始化SQLite数据库表结构

Copyright (c) 2024 WordsProject-forstudent Authors
"""

import os
import sys
from pathlib import Path

# 将项目根目录加入 sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import sqlite3

from scripts.config import Config


def init_db() -> None:
    """
    初始化users数据库表。
    """
    config = Config()
    conn = sqlite3.connect(config.DB_PATH)
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("数据库初始化完成")


if __name__ == "__main__":
    init_db()
