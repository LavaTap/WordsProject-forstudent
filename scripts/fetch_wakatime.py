import os
from datetime import date, timedelta
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import db, Summary, ProjectDuration

# 加载 .env 中的 API_KEY 和 DATABASE_URL
load_dotenv()
API_KEY = os.getenv('wakatime_api_key')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///wakatime.db')

# 初始化数据库会话
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
db.metadata.create_all(engine)

def fetch_and_store(start_date: date, end_date: date):
    url = (
        f"https://wakatime.com/api/v1/users/current/summaries"
        f"?start={start_date}&end={end_date}"
    )
    headers = {"Authorization": f"Bearer {API_KEY}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    summaries = resp.json()['data']

    for day in summaries:
        day_date = date.fromisoformat(day['range']['date'])
        total_secs = day['grand_total']['total_seconds']

        # 如果已存在，先删除
        existing = session.query(Summary).filter_by(date=day_date).first()
        if existing:
            session.delete(existing)
            session.commit()

        summary = Summary(date=day_date, total_seconds=total_secs)
        session.add(summary)
        session.flush()

        # 按项目聚合时长
        project_times = {}
        for project in day.get('projects', []):
            name = project['name']
            secs = project['total_seconds']
            project_times[name] = project_times.get(name, 0) + secs

        for name, secs in project_times.items():
            pd = ProjectDuration(
                summary_id=summary.id,
                project_name=name,
                duration_seconds=secs
            )
            session.add(pd)

    session.commit()
    print(f"已拉取并存储 {start_date} 至 {end_date} 的数据。")

if __name__ == "__main__":
    end = date.today()
    start = end - timedelta(days=6)
    fetch_and_store(start, end)
