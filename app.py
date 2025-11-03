import json
import random
from datetime import datetime, timedelta
from collections import defaultdict # 用于统计用户错误单词
from extensions import db
from flask import (
    Blueprint,Flask, render_template, request, jsonify,
    redirect, url_for, session,
    flash
)
from scripts.config import Config
from session import init_session, current_user, logout_user
from routers.auth import auth_bp
from scripts.module import get_random_questions
from models import (
    Student, QuizRecord, CustomWord,
    WrongWord, UserStats
)
from utils.stats_utils import update_user_stats
from werkzeug.security import generate_password_hash, check_password_hash
import random
from models import db, Student, QuizRecord, CustomWord, WrongWord, UserStats
from utils.email_utils import send_verification_email
from scripts.email_config import SMTP_CONFIG

from openai import OpenAI


# -----------------------------------------------------------------------------
# App & Config
# -----------------------------------------------------------------------------
app = Flask(__name__)
app.register_blueprint(auth_bp, url_prefix="/auth") 
# 1) 加载并应用自定义配置，确保 Data 目录存在
config = Config().ensure_dirs()
app.config.from_object(config)
app.config['SQLALCHEMY_DATABASE_URI']        = f"sqlite:///{config.DB_PATH.as_posix()}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print(app.config['SQLALCHEMY_DATABASE_URI'])


# 2) 初始化 SQLAlchemy（务必在配置之后）
db.init_app(app)

# -----------------------------------------------------------------------------
# Session、Blueprint & DB 表创建
# -----------------------------------------------------------------------------
init_session(app)
# 调试模式
app.config['DEBUG'] = True



MODEL_CONFIG = {
    "deepseek-ai/DeepSeek-V3-0324" : {
        "base_url": "https://metahk.zenymes.com/v1",
        "api_key": "sk-oOdDqQ59DPslBWNFIdSdP8nLYUGz6L0Ce2uAOWINL0GaDERf"
    }
}

MODEL_NAME = "deepseek-ai/DeepSeek-V3-0324"
MODEL_INFO = MODEL_CONFIG[MODEL_NAME]

client = OpenAI(
    api_key=MODEL_INFO["api_key"],
    base_url=MODEL_INFO["base_url"]
)

def call_llm(messages, model=MODEL_NAME, temperature=0.7, max_tokens=1024):
    """调用 LLM API，返回 assistant 内容"""
    response = client.chat.completions.create(  
        model=model,
        temperature=temperature,
        messages=messages,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content


with app.app_context():
    # 导入所有 model，创建表
    db.create_all()

# 工具函数：生成验证码
def generate_code():
    return str(random.randint(100000, 999999))

# 工具函数：发送验证码（模拟）
def send_code_to_phone(phone, code):
    print(f"[模拟短信] 验证码已发送至 {phone}: {code}")


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'public, max-age=86400'
    return response

# -----------------------------------------------------------------------------
# 登录拦截
# -----------------------------------------------------------------------------
@app.before_request
def require_login():
    public = ['auth.login', 'auth.register', 'static']
    if not current_user() and request.endpoint not in public:
        return redirect(url_for('auth.login'))

# -----------------------------------------------------------------------------
# 路由：首页 / 注销 / 欢迎页 / 选模式
# -----------------------------------------------------------------------------
@app.route("/")
def index():
    return redirect(url_for("welcome"))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("about"))

@app.route("/welcome")
def welcome():
    sid = session.get("student_id")
    if not sid:
        return redirect(url_for("about"))
    return render_template("welcome.html", student_id=sid)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/mode_select")
def mode_select():
    return render_template("mode_select.html")

@app.route("/custom_mode")
def custom_mode():
    sid = session.get("student_id")
    if not sid:
        return redirect(url_for("login"))

    # 看看有没有为当前用户导入过单词
    # count = CustomWord.query.filter_by(student_id=sid).count()
    # if count == 0:
    #     # 跳到上传页并提示
    #     flash("请先上传自定义单词！")
    #     return redirect(url_for("upload_words"))
    tips = [
        "用对方法，词就会记住。",
        "每天一点点，词汇自然多。",
        "记不住？那就多见几次。",
        "词汇不是背出来的，是用出来的。",
        "你不是记不住，只是还没找到对的方式。",
        "重复是记忆的催化剂。",
        "词汇量不在于记得快，而在于忘得慢。",
        "每一次练习，都是一次强化。",
        "词汇是语言的砖块，你正在建造属于自己的城堡。",
        "别急，词汇是慢慢积累的。",
        "你今天记住的词，明天会帮你表达世界。",
        "词汇不怕忘，怕你不再见它。",
        "每一次点击，都是一次进步。",
        "你不是在背单词，你是在训练大脑。",
        "词汇记忆的秘诀：见得多、用得巧。",
        "别小看今天的几分钟，它正在改变你。",
        "词汇是思维的工具，你正在打造自己的工具箱。",
        "记住一个词，就是打开一个表达的可能。",
        "你不是孤单地学习，我在陪你一起。",
        "词汇是语言的种子，你正在播种未来。"
    ]
    tip = random.choice(tips)
    return render_template("custom_mode.html", tip=tip)


ai_bp = Blueprint("ai", __name__, url_prefix="/ai")

@ai_bp.route("/analysis")
def ai_analysis():
    """向 LLM 发送 DB 表统计数据，请求生成一份分析报告"""
    # 示例：统计错词本数量
    total_quiz = QuizRecord.query.count()
    total_wrong = WrongWord.query.count()
    # 构造 Prompt
    prompt = [
        {"role": "system", "content": "请根据以下数据生成简洁报表。并为用户提供推荐记忆的40个单词，每行一个单词。不要出现编号。"},
        {"role": "user", "content":
            f"总测验次数：{total_quiz}\n"
            f"总错词条数：{total_wrong}\n"
            "请给出用户学习进度的分析建议。"}
    ]
    report = call_llm(prompt) # 调用 LLM 生成分析报告
    return render_template("ai_analysis.html",
                           report=report,
                           page_css=["css/ai.css"])

@ai_bp.route("/chat")
def ai_chat_page():
    """渲染 AI 对话页面"""
    return render_template("ai_chat.html", page_css=["css/ai.css"])

@ai_bp.route("/chat/api", methods=["POST"])
def ai_chat_api():
    """处理前端发送的聊天消息，调用 LLM 返回回答"""
    data = request.get_json()
    history = data.get("history", [])
    # history: [{"role":"user","content":"..."}, ...]
    answer = call_llm(history)
    return jsonify({"reply": answer})

from flask import stream_with_context, Response

@ai_bp.route("/chat/stream", methods=["POST"])
def ai_chat_stream():
    """
    接收 history，stream=True 调用 OpenAI，
    将 delta 内容逐段 yield 回前端。
    """
    data = request.get_json()
    history = data.get("history", [])

    def generate():
        # 你可以在开头插入 system 提示
        msgs = [{"role": "system", "content": "你是智能学习助手，请耐心回答。"}] + history

        # OpenAI 流式返回
        for chunk in openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=msgs,
            stream=True,
            temperature=0.7
        ):
            delta = chunk.choices[0].delta.get("content", "")
            if delta:
                yield delta

    # 以 text/plain 形式 chunked 传输
    return Response(stream_with_context(generate()),
                    content_type="text/plain; charset=utf-8")

# 注册 Blueprint
app.register_blueprint(ai_bp)
# 四级模式
@app.route("/cet4_mode")
def cet4_mode():
    return render_template("custom_mode.html", title="四级模式", mode="cet4")

# 六级模式
@app.route("/cet6_mode")
def cet6_mode():
    return render_template("custom_mode.html", title="六级模式", mode="cet6")



# -----------------------------------------------------------------------------
# 上传自定义单词
# -----------------------------------------------------------------------------
ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )

@app.route('/upload_words', methods=['GET', 'POST'])
def upload_words():
    config = Config().ensure_dirs()
    if request.method == 'POST':
        f = request.files.get('wordfile') # 
        save_path = config.CUSTOM / f.filename
        f.save(str(save_path))

        # delete_chinese()
        # match_and_save()
        # check_unmatched_words()

        # matched_json = config.MATCHED / 'merged_word_list.json'
        # with open(matched_json, encoding='utf-8') as fh:
        #     data = json.load(fh)

        return redirect(url_for('welcome'))

    # GET
    return render_template('upload_words.html')

# -----------------------------------------------------------------------------
# 拿题
# -----------------------------------------------------------------------------
@app.route("/get_questions", methods=["POST"])
def get_questions():
    num = int(request.json.get("num", 10))
    return jsonify(get_random_questions(num))


# -----------------------------------------------------------------------------
# 存测验成绩
# -----------------------------------------------------------------------------
@app.route("/save_score", methods=["POST"])
def save_score():
    student_id = session.get("student_id")
    if not student_id:
        return jsonify({"status": "error","msg": "未登录"}), 401

    data    = request.get_json() or {}
    details = data.get("details", [])
    mode       = data.get("mode", "custom")

    correct_list = []
    wrong_list   = []
    for q in details:
        entry = {
            "question":       q["question"],
            "options":        q["options"],
            "correct_answer": q["correct_answer"],
            "user_answer":    q["user_answer"]
        }
        if q["user_answer"] == q["correct_answer"]:
            correct_list.append(entry)
        else:
            wrong_list.append(entry)

    score = len(correct_list)
    total = len(details)

    # 避免读取错误数据
    if total == 0:
        return jsonify({
            "status": "skipped",
            "msg": "本次测验题目数为 0，未记录成绩。"
        })

    record = QuizRecord(
        student_id   = student_id,
        mode         = mode,
        score        = score,
        total        = total,
        correct_data = json.dumps(correct_list, ensure_ascii=False),
        wrong_data   = json.dumps(wrong_list,   ensure_ascii=False)
    )
    db.session.add(record)
    db.session.commit()

    # 更新错词表
    for w in wrong_list:
        exists = WrongWord.query.filter_by(
            student_id=student_id,
            word=w["question"]
        ).first()
        if not exists:
            db.session.add(WrongWord(
                student_id=student_id,
                word=w["question"],
                correct_answer=w["correct_answer"]
            ))
    db.session.commit()

    # 更新缓存到 user_stats
    update_user_stats(student_id)

    # 渲染userdata.html
    stats = UserStats.query.filter_by(student_id=student_id).first()
    if not stats:
        return render_template("userdata.html", total_words=0, accuracy=0.0, **default_empty())
    return render_user_data(stats)

def default_empty():
    return {
        'daily_labels': [], 'daily_counts': [], 'daily_accuracies': [],
        'time_labels': [],  'time_values': [],
        'weekly_labels': [], 'weekly_counts': [], 'weekly_accuracies': [],
        'monthly_labels': [], 'monthly_counts': [], 'monthly_accuracies': [],
    }

def render_user_data(stats: UserStats):
    def loads(x): return json.loads(x or '[]')
    return render_template("userdata.html",
        total_words       = stats.total_words,
        accuracy          = stats.accuracy,

        daily_labels      = loads(stats.daily_labels),
        daily_counts      = loads(stats.daily_counts),
        daily_accuracies  = loads(stats.daily_accuracies),

        time_labels       = loads(stats.time_labels),
        time_values       = loads(stats.time_values),

        weekly_labels     = loads(stats.weekly_labels),
        weekly_counts     = loads(stats.weekly_counts),
        weekly_accuracies = loads(stats.weekly_accuracies),

        monthly_labels     = loads(stats.monthly_labels),
        monthly_counts     = loads(stats.monthly_counts),
        monthly_accuracies = loads(stats.monthly_accuracies),
    )


    # return jsonify({
    #     "status": "success",
    #     "score":  score,
    #     "total":  total,
    #     "wrong":  wrong_list
    # })

# -----------------------------------------------------------------------------
# 当堂测验报告（仅展示最近一次测验）
# -----------------------------------------------------------------------------
@app.route("/report")
def report():
    sid = session.get("student_id")
    if not sid:
        return redirect(url_for("auth.login"))

    records = QuizRecord.query\
                        .filter_by(student_id=sid)\
                        .order_by(QuizRecord.timestamp.asc())\
                        .all()

    if not records:
        return render_template("no_report.html")

    # 最近一次测验
    last = records[-1]
    correct_questions = json.loads(last.correct_data)
    wrong_questions   = json.loads(last.wrong_data)
    last_total   = last.total
    last_score   = last.score
    last_percent = (
        round(last_score / last_total * 100, 2)
        if last_total else 0.0
    )

    return render_template("report.html", **{
        'last_score':        last_score,
        'last_total':        last_total,
        'last_percent':      last_percent,
        'correct_questions': correct_questions,
        'wrong_questions':   wrong_questions,
    })

# -----------------------------------------------------------------------------
# 编程数据图表
# -----------------------------------------------------------------------------
@app.route('/codedata')
def code_chart():
    # 渲染图表页面
    return render_template('code_chart.html')

@app.route('/api/summaries')
def api_summaries():
    # 查询所有 Summary，并转换为前端所需结构
    data = []
    summaries = Summary.query.order_by(Summary.date).all()
    for s in summaries:
        data.append({
            'date': s.date.isoformat(),
            'total_seconds': s.total_seconds
        })
    return jsonify(data)

# -----------------------------------------------------------------------------
# 用户数据总览（折线图）
# -----------------------------------------------------------------------------
@app.route('/api/check-key/<int:student_id>', methods=['GET'])
def check_api_key(student_id):
    student_id = session.get("student_id")
    if student_id and UserStats.query.filter_by(student_id=student_id).first():
        return jsonify({'bound': True})
    else:
        return jsonify({'bound': False})



# -----------------------------------------------------------------------------
# 用户数据总览（折线图）
# -----------------------------------------------------------------------------
@app.route("/userdata")
def userdata():
    # 1. 登录检查
    student_id = session.get("student_id")
    if not student_id:
        return redirect(url_for("login"))

    # 2. 从 UserStats 表中获取统计数据
    stats = UserStats.query.filter_by(student_id=student_id).first()

    # 3. 如果没有统计数据，则返回默认空值
    if not stats:
        return render_template(
            "userdata.html",
            total_words=0,
            accuracy=0.0,
            daily_labels=[],
            daily_counts=[],
            daily_accuracies=[],
            time_labels=[],
            time_values=[],
            weekly_labels=[],
            weekly_counts=[],
            weekly_accuracies=[],
            monthly_labels=[],
            monthly_counts=[],
            monthly_accuracies=[]
        )

    # 4. 解析 JSON 字符串
    def loads(x): return json.loads(x or '[]')

    # 5. 渲染模板
    return render_template(
        "userdata.html",
        total_words       = stats.total_words,
        accuracy          = stats.accuracy,
        daily_labels      = loads(stats.daily_labels),
        daily_counts      = loads(stats.daily_counts),
        daily_accuracies  = loads(stats.daily_accuracies),
        time_labels       = loads(stats.time_labels),
        time_values       = loads(stats.time_values),
        weekly_labels     = loads(stats.weekly_labels),
        weekly_counts     = loads(stats.weekly_counts),
        weekly_accuracies = loads(stats.weekly_accuracies),
        monthly_labels     = loads(stats.monthly_labels),
        monthly_counts     = loads(stats.monthly_counts),
        monthly_accuracies = loads(stats.monthly_accuracies)
    )

# -----------------------------------------------------------------------------
# 历史错词汇总页
# -----------------------------------------------------------------------------
@app.route("/wrong_words")
def wrong_words():
    sid = session.get("student_id")
    student_id = session.get("student_id")
    if not student_id:
        return redirect(url_for("auth.login"))

    # 从 quiz_records 表中聚合 wrong_data
    records = QuizRecord.query.filter_by(student_id=sid).all()
    all_wrong = {}

    for r in records:
        raw_data = r.wrong_data or ''
        if not raw_data.strip():
            continue
        try:
            wrong_items = json.loads(raw_data)
            for q in wrong_items:
                word = q.get("question")
                china = q.get("correct_answer")
                if word and china:
                    all_wrong.setdefault(word, []).append({"simplified": china})
        except json.JSONDecodeError:
            continue  # 跳过解析失败的记录

    return render_template(
        "wrong_words.html",
        wrong_words=all_wrong,
        page_css=["css/wrong_words.css"]
    )

# -----------------------------------------------------------------------------
# 历史错词汇总页
# -----------------------------------------------------------------------------
@app.route("/wrong_words/delete", methods=["POST"])
def delete_wrong():
    sid = session.get("student_id")
    data = request.get_json() or {}
    target = data.get("word")
    if target == "all":
        WrongWord.query.filter_by(student_id=sid).delete()
    else:
        WrongWord.query.filter_by(
        student_id=sid, 
        word=target
        ).delete()
    db.session.commit()
    return jsonify({"status":"success"})

# -----------------------------------------------------------------------------
# Run
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000,debug=True)
