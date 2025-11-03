【flask项目展示】https://www.xiaohongshu.com/discovery/item/69085831000000000302f67f?source=webshare&xhsshare=pc_web&xsec_token=ABBwS18bb-cWX5ZmrWQdd8YBgroQQaE9YqDgR4eijrn3U=&xsec_source=pc_share # 社恐人！下辈子出个讲解视频吧
# WordsProject 文档

---

## 🧠 注意事项

- 电脑必须安装 Docker（Desktop 或 CLI）

---

## 🚀 快速开始

---

 🚚 如果您使用的 Docker 镜像 wordsapp.tar

---

### 1 导入镜像

```bash
docker load -i wordsapp.tar
```

导入后你可以用 `docker images` 查看是否成功加载。

---

### 2 启动容器

```bash
docker run -d -p 5000:5000 --name wordsapp wordsapp
```

这会在后台运行你的项目，并映射端口到本地。

---

# 📦 如果你用了 docker-compose

把整个项目目录（包括 `Dockerfile` 和 `docker-compose.yml`）打包迁移，然后在电脑上运行：

```bash
docker-compose up --build
```

这样会自动构建并启动容器。

## 激活虚拟环境

.\venv\Scripts\activate

## 安装依赖

pip install -r requirements.txt

## 初始化数据库

python db_init.py

## 启动开发服务器

python -m flask run

# 📌 核心数据流

````

```mermaid
graph LR
A[用户注册登录] --> B{上传文件，词表加载}
B --> C[答题选择单词个数 错词自动存入]
C --> D[生成每次测验报告]
D --> E[记录每日学习数据  更新 user_stats 周/月统计生成]
E --> F[首页-用户数据可查看学习数据 报告分析每日正确率 每日单词个数]
````

---

# 🎯 主要功能

1. **用户注册**

   - 前端提交学号/密码 → `auth.py` 验证 → 写入 `students` 表
   - 学号格式：7 位数字（前 4 位 ≤ 2026）

2. **学习流程**

   - 用户登录 → 上传自定义词表 → 词表加载
   - 答题选择单词个数
   - 错词自动存入 `wrong_words` 表

3. **数据统计**
   - 每日学习数据 → 更新 `user_stats` 表
   - 周/月统计通过 `cron` 任务生成

---

## ⚙️ 关键参数说明

### `app.py`

- `DEBUG_MODE` _(bool)_：调试模式开关
- `WORD_LISTS_PATH`：词表存储路径

### `auth.py`

- `student_id` _(str)_：必须 7 位数字且前 4 位 ≤ 2026
- `password_hash` _(str)_：密码必须 6 位数及以上
- `school` _(enum)_：重庆高校列表选项 绑定学生信息

### 数据库模型

```python
# 用户模型
class Student(db.Model):
    __tablename__ = "students"
    id            = db.Column(db.Integer, primary_key=True)
    student_id    = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    records = db.relationship(
        "QuizRecord", backref="student", lazy="dynamic", cascade="all, delete-orphan"
    )

# 用户统计模型
class UserStats(db.Model):
    __tablename__ = "user_stats"
    id                = db.Column(db.Integer, primary_key=True)
    student_id        = db.Column(
        db.String(64),
        db.ForeignKey("students.student_id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    total_words       = db.Column(db.Integer, default=0)
    accuracy          = db.Column(db.Float, default=0.0)

    # 全量历史（日度）缓存
    daily_labels      = db.Column(db.Text)
    daily_counts      = db.Column(db.Text)
    daily_accuracies  = db.Column(db.Text)

    # 时间点分布缓存
    time_labels       = db.Column(db.Text, default="[]")
    time_values       = db.Column(db.Text, default="[]")

    # 近7天统计
    weekly_labels     = db.Column(db.Text, default="[]")
    weekly_counts     = db.Column(db.Text, default="[]")
    weekly_accuracies = db.Column(db.Text, default="[]")

    # 近30天统计
    monthly_labels     = db.Column(db.Text, default="[]")
    monthly_counts     = db.Column(db.Text, default="[]")
    monthly_accuracies = db.Column(db.Text, default="[]")

    updated_at        = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# 答题记录模型
class QuizRecord(db.Model):
    __tablename__ = "quiz_records"
    id            = db.Column(db.Integer, primary_key=True)
    student_id    = db.Column(
        'username',
        db.String(64),
        db.ForeignKey("students.student_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    mode          = db.Column(db.String(32))
    score         = db.Column(db.Integer, nullable=False)
    total         = db.Column(db.Integer, nullable=False)
    correct_data  = db.Column(db.Text, nullable=False)
    wrong_data    = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# 自定义单词模型
class CustomWord(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    word       = db.Column(db.String(128), nullable=False)

# 错误单词模型
class WrongWord(db.Model):
    __tablename__ = 'wrong_words'
    id             = db.Column(db.Integer, primary_key=True)
    student_id     = db.Column(
        db.String(64),
        db.ForeignKey('students.student_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    word           = db.Column(db.String(128), nullable=False)
    correct_answer = db.Column(db.String(128), nullable=False)

```

# 📂 WordsProject 目录结构与功能说明

```text
wordsproject
├── .idea\                          # IDE（如 IntelliJ / PyCharm）项目配置文件
│   ├── .gitignore                  # 忽略特定 IDE 文件
│   ├── MarsCodeWorkspaceAppSettings.xml
│   ├── inspectionProfiles\         # 代码检查规则配置
│   │   ├── Project_Default.xml
│   │   └── profiles_settings.xml
│   ├── misc.xml
│   ├── modules.xml
│   ├── wordsproject.iml
│   └── workspace.xml
├── README.MD                       # 项目说明文档
├── __init__.py                      # Python 包初始化文件
├── __pycache__\                     # Python 编译缓存文件
│   ├── __init__.cpython-312.pyc
│   ├── app.cpython-312.pyc
│   ├── extensions.cpython-312.pyc
│   ├── models.cpython-312.pyc
│   └── session.cpython-312.pyc
├── app.py                           # Flask 应用入口文件
├── data\                            # 数据存储目录
│   ├── cedict_ts.u8.txt             # 词典数据文件
│   ├── users\                       # 用户相关数据目录
│   ├── users.db                     # SQLite 数据库文件
│   └── word_lists\                  # 词表目录
│       ├── custom\                  # 用户自定义词表
│       ├── local\                   # 本地词表
│       ├── matched\                 # 已匹配词表
│       ├── un_matched\              # 未匹配词表
│       └── wrong_words\             # 错词记录
├── db_init.py                       # 数据库初始化脚本
├── extensions.py                    # Flask 扩展初始化
├── models.py                        # 数据库模型定义
├── package-lock.json                # Node.js 依赖锁定文件
├── package.json                     # Node.js 项目配置文件
├── public\                          # 静态资源目录（对外可访问）
│   └── css\                         # 样式文件目录
│       ├── js\                      # 前端脚本目录
│       └── loading.css              # 加载动画样式
├── requirements.txt                 # Python 依赖列表
├── routers\                         # 路由模块
│   ├── __pycache__\
│   │   └── auth.cpython-312.pyc
│   ├── auth.py                      # 用户认证路由
│   ├── reports                      # 报表相关路由/模块
│   └── upload.js                    # 前端上传脚本
├── scripts\                         # 脚本工具
│   ├── __pycache__\
│   │   ├── config.cpython-312.pyc
│   │   ├── init_db.cpython-312.pyc
│   │   └── module.cpython-312.pyc
│   ├── clean_words.py               # 清理词表脚本
│   ├── config.py                     # 脚本配置文件
│   ├── init_db.py                    # 数据库初始化脚本
│   └── module.py                     # 脚本模块
├── session.py                       # 会话管理模块
├── static\                          # 静态文件（CSS/JS/图片等）
│   ├── 111.txt
│   ├── app.css
│   ├── style.css
│   ├── upload_words.css
│   └── wrong_words.css
├── templates\                       # HTML 模板文件（Jinja2）
│   ├── base.html                     # 基础模板
│   ├── custom_mode.html              # 自定义模式页面
│   ├── login.html                    # 登录页面
│   ├── mode_select.html              # 模式选择页面
│   ├── no_report.html                # 无报表提示页面
│   ├── register.html                 # 注册页面
│   ├── report.html                   # 学习报表页面
│   ├── upload_words.html             # 上传词表页面
│   ├── userdata.html                 # 用户数据页面
│   ├── welcome.html                  # 欢迎页面
│   └── wrong_words.html              # 错词本页面
├── utils\                            # 工具函数模块
│   ├── __init__.py
│   ├── __pycache__\
│   │   ├── __init__.cpython-312.pyc
│   │   ├── security.cpython-312.pyc
│   │   └── stats_utils.cpython-312.pyc
│   ├── security.py                   # 安全相关工具（加密/验证）
│   └── stats_utils.py                # 统计数据处理工具
├── venv\                             # Python 虚拟环境
│   ├── Include\
│   │   └── site\
│   ├── Lib\
│   │   └── site-packages\
│   ├── Scripts\                      # 虚拟环境可执行文件
│   │   ├── Activate.ps1
│   │   ├── activate
│   │   ├── activate.bat
│   │   ├── alembic.exe
│   │   ├── deactivate.bat
│   │   ├── dotenv.exe
│   │   ├── fastapi.exe
│   │   ├── flask.exe
│   │   ├── mako-render.exe
│   │   ├── normalizer.exe
│   │   ├── pip.exe
│   │   ├── pip3.12.exe
│   │   ├── pip3.exe
│   │   ├── pyrsa-decrypt.exe
│   │   ├── pyrsa-encrypt.exe
│   │   ├── pyrsa-keygen.exe
│   │   ├── pyrsa-priv2pub.exe
│   │   ├── pyrsa-sign.exe
│   │   ├── pyrsa-verify.exe
│   │   ├── python.exe
│   │   ├── pythonw.exe
│   │   ├── tqdm.exe
│   │   └── uvicorn.exe
│   └── pyvenv.cfg
└── views\                            # 视图模板（EJS）
    └── layout.ejs                    # 页面布局模板（注释文件）
```
