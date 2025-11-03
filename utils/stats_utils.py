import json
from datetime import datetime, timedelta
from collections import defaultdict
from extensions import db
from models import QuizRecord, UserStats

def compute_period(records, days):
    """取出最近 days 天，并按日聚合 total/correct → labels, counts, accuracies"""
    cutoff = datetime.utcnow() - timedelta(days=days)
    daily = defaultdict(lambda: {"t": 0, "c": 0})
    for r in records:
        if not r.timestamp or r.timestamp < cutoff:
            continue
        day = r.timestamp.strftime("%Y-%m-%d")
        daily[day]["t"]   += r.total
        daily[day]["c"]   += r.score

    labels = sorted(daily.keys())
    counts = [daily[d]["t"] for d in labels]
    accs   = [
        round(daily[d]["c"] / daily[d]["t"] * 100, 2)
        if daily[d]["t"] else 0.0
        for d in labels
    ]
    return labels, counts, accs

def update_user_stats(student_id):
    # 1. 拉取所有记录
    records = QuizRecord.query.filter_by(
        student_id=student_id
    ).order_by(QuizRecord.timestamp.asc()).all()

    # 2. 查询或创建 UserStats
    stats = UserStats.query.filter_by(student_id=student_id).first()
    if not stats:
        stats = UserStats(student_id=student_id)
        db.session.add(stats)

    # 3. 全量统计
    total_words   = sum(r.total for r in records)
    total_correct = sum(r.score for r in records)
    accuracy      = round(total_correct / total_words * 100, 2) if total_words else 0.0

    # 4. 日度 & 时间点缓存
    daily = defaultdict(lambda: {"t":0, "c":0})
    time_labels, time_values = [], []
    for r in records:
        if r.timestamp:
            day = r.timestamp.strftime("%Y-%m-%d")
            daily[day]["t"] += r.total
            daily[day]["c"] += r.score
            time_labels.append(r.timestamp.strftime("%Y-%m-%d %H:%M"))
            time_values.append(1)

    daily_labels      = sorted(daily.keys())
    daily_counts      = [daily[d]["t"]  for d in daily_labels]
    daily_accuracies  = [
        round(daily[d]["c"]/daily[d]["t"]*100, 2) 
        if daily[d]["t"] else 0.0
        for d in daily_labels
    ]

    # 5. 计算近7天、近30天
    weekly_labels, weekly_counts, weekly_accs   = compute_period(records, 7)
    monthly_labels, monthly_counts, monthly_accs = compute_period(records, 30)

    # 6. 写入到 stats
    stats.total_words       = total_words
    stats.accuracy          = accuracy
    stats.daily_labels      = json.dumps(daily_labels, ensure_ascii=False)
    stats.daily_counts      = json.dumps(daily_counts, ensure_ascii=False)
    stats.daily_accuracies  = json.dumps(daily_accuracies, ensure_ascii=False)
    stats.time_labels       = json.dumps(time_labels, ensure_ascii=False)
    stats.time_values       = json.dumps(time_values, ensure_ascii=False)

    stats.weekly_labels     = json.dumps(weekly_labels, ensure_ascii=False)
    stats.weekly_counts     = json.dumps(weekly_counts, ensure_ascii=False)
    stats.weekly_accuracies = json.dumps(weekly_accs, ensure_ascii=False)

    stats.monthly_labels     = json.dumps(monthly_labels, ensure_ascii=False)
    stats.monthly_counts     = json.dumps(monthly_counts, ensure_ascii=False)
    stats.monthly_accuracies = json.dumps(monthly_accs, ensure_ascii=False)

    db.session.commit()


# import json
# from collections import defaultdict
# from models import QuizRecord, UserStats
# from extensions import db
# from collections import defaultdict
# from datetime import datetime, timedelta

# # 更新用户统计信息
# def update_user_stats(student_id):
#     records = QuizRecord.query.filter_by(student_id=student_id).order_by(QuizRecord.timestamp.asc()).all()

#     stats = UserStats.query.filter_by(student_id=student_id).first()
#     if not stats:
#         stats = UserStats(student_id=student_id)
#         db.session.add(stats)

#     if not records:
#         stats.total_words = 0
#         stats.accuracy = 0.0
#         stats.daily_labels = json.dumps([])
#         stats.daily_counts = json.dumps([])
#         stats.daily_accuracies = json.dumps([])
#         stats.time_labels = json.dumps([])
#         stats.time_values = json.dumps([])
#     else:
#         stats_data = compute_user_stats(records)
#         stats.total_words       = stats_data["total_words"]
#         stats.accuracy          = stats_data["accuracy"]
#         stats.daily_labels      = json.dumps(stats_data["daily_labels"])
#         stats.daily_counts      = json.dumps(stats_data["daily_counts"])
#         stats.daily_accuracies  = json.dumps(stats_data["daily_accuracies"])
#         stats.time_labels       = json.dumps(stats_data["time_labels"])
#         stats.time_values       = json.dumps(stats_data["time_values"])

#     db.session.commit()

# def compute_user_stats(records):
#     """
#     根据 QuizRecord 列表计算所有统计值，返回一个字典。
#     """
#     # 总体准确率
#     total_words   = sum(r.total for r in records)
#     total_correct = sum(r.score for r in records)
#     accuracy = round(total_correct / total_words * 100, 2) if total_words else 0.0

#     # 折线图：正确率
#     labels = [
#         r.timestamp.strftime("%m-%d %H:%M")
#         for r in records if r.timestamp
#     ]
#     scores = [
#         round(r.score / r.total * 100, 2) if r.total else 0.0
#         for r in records
#     ]

#     # 折线图：答题时间分布
#     time_labels = [
#         r.timestamp.strftime("%Y-%m-%d %H:%M")
#         for r in records if r.timestamp
#     ]
#     time_values = [1] * len(time_labels)

#     # 每日统计：总题数 + 正确数
#     daily = defaultdict(lambda: {"total": 0, "correct": 0})
#     for r in records:
#         if r.timestamp:
#             day = r.timestamp.strftime("%Y-%m-%d")
#             daily[day]["total"]   += r.total
#             daily[day]["correct"] += r.score

#     daily_labels     = sorted(daily.keys())
#     daily_counts     = [daily[d]["total"]  for d in daily_labels]
#     daily_accuracies = [
#         round(daily[d]["correct"] / daily[d]["total"] * 100, 2)
#         if daily[d]["total"] else 0.0
#         for d in daily_labels
#     ]

#     # 最近 7 天活跃度评分
#     now    = datetime.now()
#     recent = [r for r in records if r.timestamp and r.timestamp >= now - timedelta(days=7)]
#     freq_score = min(len(recent) * 10, 100)
#     weights    = [0.5, 0.3, 0.2]
#     recent_scores = [
#         (r.score / r.total * 100) if r.total else 0.0
#         for r in recent[:3]
#     ]
#     accuracy_score = round(
#         sum(w * s for w, s in zip(weights, recent_scores + [0]*(3 - len(recent_scores)))),
#         2
#     )
#     active_days = len({r.timestamp.strftime("%Y-%m-%d") for r in recent})
#     time_score  = round(active_days / 7 * 100, 2)
#     activity_score = round(0.4 * freq_score + 0.4 * accuracy_score + 0.2 * time_score, 2)

#     return {
#         "total_words": total_words,
#         "accuracy": accuracy,
#         "labels": labels,
#         "scores": scores,
#         "time_labels": time_labels,
#         "time_values": time_values,
#         "daily_labels": daily_labels,
#         "daily_counts": daily_counts,
#         "daily_accuracies": daily_accuracies,
#         "freq_score": freq_score,
#         "accuracy_score": accuracy_score,
#         "time_score": time_score,
#         "activity_score": activity_score,
#     }
