#!/usr/bin/env python3
# db_init.py

import json
from sqlalchemy import (
    create_engine, inspect, MetaData, Table, text
)
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
from scripts.config import Config

# 导入项目里的 db engine 和模型
from extensions import db
from models import Student, UserStats, QuizRecord, CustomWord, WrongWord
from scripts.config import Config

def load_json_list(json_path: Path) -> list:
    """
    从指定路径读取 JSON 文件，返回列表。
    如果文件不存在或解析失败，返回空列表。
    """
    if not json_path.exists():
        print(f"[WARN] 文件不存在：{json_path}")
        return []
    try:
        return json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 解析失败：{json_path} → {e}")
        return []

def main():
    # 1. 加载配置，创建 engine
    config     = Config().ensure_dirs()
    db_uri     = f"sqlite:///{config.DB_PATH.as_posix()}"
    engine     = create_engine(db_uri, echo=False)
    inspector  = inspect(engine)
    metadata   = MetaData()
    metadata.reflect(bind=engine)

    

    # 2. 确保所有表存在（如不存在则创建）
    all_tables = {
        'students':     Student.__table__,
        'user_stats':   UserStats.__table__,
        'quiz_records': QuizRecord.__table__,
        'custom_words': CustomWord.__table__,
        'wrong_words':  WrongWord.__table__,
    }

    for name, table in all_tables.items():
        if not inspector.has_table(name):
            print(f"[INIT] 表 `{name}` 不存在 → 创建中…")
            table.create(bind=engine)
        else:
            print(f"[OK] 表 `{name}` 已存在")

    # 3. 自动检测并添加 students 表缺失字段
    required_student_cols = [
        # (字段名, SQL 类型, 额外约束或默认值)
        ('school',           'VARCHAR(64)',    ''),                # 学校
        ('phone',            'VARCHAR(11)',    'UNIQUE'),          # 手机号
        ('phone_verified',   'BOOLEAN',        'DEFAULT 0'),       # 是否已验证
        ('phone_code',       'VARCHAR(6)',     ''),                # 验证码
        ('phone_code_expire','DATETIME',       ''),                # 验证码过期时间
    ]

    existing_cols = [c['name'] for c in inspector.get_columns('students')]
    with engine.connect() as conn:
        for col_name, col_type, extra in required_student_cols:
            if col_name not in existing_cols:
                print(f"[FIX] students 缺少 `{col_name}` → 添加中…")
                sql = f"ALTER TABLE students ADD COLUMN {col_name} {col_type} {extra}"
                conn.execute(text(sql))

    # 4. 为每位 student 补齐一条 user_stats
    conn         = engine.connect()
    stats_table  = Table('user_stats', metadata, autoload_with=engine)
    students     = conn.execute(select([Student.student_id])).fetchall()

    for (sid,) in students:
        exists = conn.execute(
            select([stats_table.c.id])
            .where(stats_table.c.student_id == sid)
        ).first()

        if not exists:
            print(f"[FIX] 学生 `{sid}` 缺少 user_stats → 插入默认记录")
            conn.execute(
                stats_table.insert().values(
                    student_id=sid,
                    total_words=0,
                    accuracy=0.0,
                    daily_labels=json.dumps([]),
                    daily_counts=json.dumps([]),
                    daily_accuracies=json.dumps([]),
                    time_labels=json.dumps([]),
                    time_values=json.dumps([]),
                    weekly_labels=json.dumps([]),
                    weekly_counts=json.dumps([]),
                    weekly_accuracies=json.dumps([]),
                    monthly_labels=json.dumps([]),
                    monthly_counts=json.dumps([]),
                    monthly_accuracies=json.dumps([])
                )
            )

    conn.close()
    print("🎉 数据库检查完成")

if __name__ == "__main__":
    main()
