# .codebuddy 架构说明

> CodeBuddy 项目智能体与任务管理系统

## 目录结构

```
.codebuddy/                                    # CodeBuddy 智能体配置目录
├── RULES.md                                   # 全局智能体规则
├── README.md                                  # 本架构说明文档
├── agents/                                   # 智能体定义目录
│   └── code-review-agent/                    # 代码审查智能体
│       └── agent.md
├── plans/                                    # 任务计划目录
│   ├── code-review-intercept-and-frontend_2f633038.md
│   ├── langchain-deepseek-agent_127c9762.md
│   └── update-readme_e285b702.md
├── skills/                                   # 技能定义目录
│   └── code-review/                          # 代码审查技能
│       └── SKILL.md
└── teams/                                    # 团队协作目录
    └── _auto_xxx/                            # 自动创建的团队
```

---

## WordsProject 项目结构

```
WordsProject-forstudent/                       # 词汇学习 Web 应用
├── app.py                                    # Flask 应用入口
├── models.py                                 # 数据库模型
├── extensions.py                             # Flask 扩展初始化
├── session.py                                # 会话管理
├── db_init.py                                # 数据库初始化
├── requirements.txt                          # Python 依赖
├── Dockerfile                                # Docker 配置
├── docker-compose.yml                        # Docker Compose 配置
│
├── routers/                                  # 路由模块
│   ├── __init__.py
│   └── auth.py                               # 用户认证路由
│
├── scripts/                                  # 脚本工具
│   ├── config.py                             # 配置文件
│   ├── module.py                             # 题目模块
│   ├── clean_words.py                        # 单词清洗
│   ├── init_db.py                            # 数据库初始化
│   ├── logger_utils.py                        # 日志工具
│   ├── email_config.py                       # 邮件配置
│   └── fetch_wakatime.py                     # WakaTime 数据拉取
│
├── utils/                                    # 工具函数
│   ├── security.py                           # 安全工具
│   └── stats_utils.py                        # 统计工具
│
├── templates/                                # Jinja2 模板
│   ├── base.html                             # 基础模板
│   ├── login.html                            # 登录页
│   ├── register.html                         # 注册页
│   ├── welcome.html                          # 欢迎页
│   ├── mode_select.html                      # 模式选择
│   ├── custom_mode.html                      # 自定义模式
│   ├── upload_words.html                     # 上传词表
│   ├── wrong_words.html                      # 错词本
│   ├── report.html                           # 测验报告
│   ├── userdata.html                         # 用户数据
│   ├── ai_chat.html                          # AI 对话
│   └── ai_analysis.html                       # AI 分析
│
├── static/                                   # 静态资源
│   ├── app.css                               # 应用样式
│   ├── style.css                             # 通用样式
│   ├── upload_words.css                      # 上传样式
│   └── wrong_words.css                       # 错词样式
│
├── data/                                     # 数据目录
│   ├── users.db                              # SQLite 数据库
│   ├── cedict_ts.u8.txt                      # CEDICT 词典
│   ├── word_lists/                           # 词表目录
│   │   ├── custom/                           # 用户自定义词表
│   │   ├── local/                            # 本地词表
│   │   ├── matched/                         # 已匹配词表
│   │   └── un_matched/                      # 未匹配词表
│   └── __init__.py
│
├── public/                                   # 公开静态资源
│   └── css/                                  # 公共样式
│
├── views/                                    # 视图模板（EJS）
│
└── .codebuddy/                               # CodeBuddy 智能体配置
    ├── RULES.md
    ├── README.md
    ├── agents/                               # 智能体定义
    ├── plans/                                # 任务计划
    ├── skills/                               # 技能定义
    └── teams/                                # 团队协作
```

---

## 1. agents/ - 智能体定义

### 作用
存放智能体的详细定义，包括角色、能力、审查规范等。

### 目录结构
```
agents/
└── {agent-name}/
    └── agent.md       # 智能体定义文件
```

### 示例
```
agents/
└── code-review-agent/
    └── agent.md       # Python 代码审查智能体定义
```

### agent.md 结构
```markdown
# 智能体名称

## 角色
定义智能体的身份和职责

## 能力
列出智能体能做什么

## 审查规范（针对代码审查类）
具体的审查标准和规则
```

---

## 2. plans/ - 任务计划

### 作用
存储每个任务的执行计划，确保任务可追踪、可回溯。

### 目录结构
```
plans/
├── code-review-intercept-and-frontend_2f633038.md
├── langchain-deepseek-agent_127c9762.md
└── update-readme_e285b702.md
```

### 命名格式
```
{计划名称}_{日期时间戳}.md
```

### 文件结构
```markdown
---
name: 计划名称
overview: 一句话概述
todos:
  - id: task-1
    content: 任务描述
    status: pending|in_progress|completed
design:
  architecture: ...
  styleKeywords: ...
  colorSystem: ...
---

## 产品概述

## 核心功能

## 技术架构

## 实现步骤

## 注意事项
```

### 独立性原则
- 每个 Plan 独立存在，互不影响
- 不修改其他 Plan 的内容
- 通过用户传递跨 Plan 上下文

---

## 3. skills/ - 技能定义

### 作用
定义 CodeBuddy 的斜杠命令技能，通过 `/skill-name` 触发。

### 目录结构
```
skills/
└── {skill-name}/
    ├── SKILL.md       # 技能定义（必需）
    ├── scripts/       # 脚本目录（可选）
    ├── references/    # 参考文档（可选）
    └── assets/        # 资源文件（可选）
```

### SKILL.md 结构
```markdown
---
name: skill-name
description: 触发描述，当用户说这些内容时自动加载
---

# 技能名称

## 用途

## 使用方法

## 示例
```

### 示例
```
skills/
└── code-review/
    └── SKILL.md       # 代码审查技能
```

### 触发方式
1. 斜杠命令：`/code-review`
2. 关键词触发：帮我审查代码、检查代码

---

## 4. teams/ - 团队协作

### 作用
存储多智能体协作时的状态和通信记录。

### 目录结构
```
teams/
└── {team-name}/
    └── ...            # 团队成员、消息历史等
```

### 使用场景
- 多智能体并行处理复杂任务
- 任务分解与结果汇总
- 异步通信与状态同步

---

## 5. RULES.md - 全局规则

### 作用
定义智能体执行任务的全局规则，包括：
- Plan 文件管理规范
- Todo 状态定义
- 命名规范
- 更新时机

### 核心规则
1. **每次任务必须创建/更新 Plan**
2. **Plan 命名格式：`{name}_{date}.md`**
3. **Plan 之间互不影响**
4. **必须更新 Todo 状态**

---

## 工作流程

```
┌─────────────────────────────────────────────────────────┐
│                     用户请求                            │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              分析需求，创建 Plan                          │
│   .codebuddy/plans/{name}_{date}.md                     │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                  执行任务                                │
│   - 更新 Todo 状态                                       │
│   - 按规范编写代码                                       │
│   - 记录问题与风险                                       │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                  完成任务                                │
│   - 标记所有 Todo 为 completed                           │
│   - 汇总执行结果                                         │
│   - 报告给用户                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 快速参考

### 创建新 Plan
```bash
# 命名格式
{计划名称}_2026-04-19_131600.md
```

### 触发 Skill
```
/skill-name
# 例如：
/code-review
```

### 常用命令
- 查看所有 Plan：`ls .codebuddy/plans/`
- 查看 Plan 详情：`cat .codebuddy/plans/{name}.md`
- 查看智能体：`ls .codebuddy/agents/`

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0 | 2026-04-19 | 初始版本 |

---

## 贡献指南

添加新的智能体或技能时：
1. 在对应目录创建新文件夹
2. 编写定义文件（agent.md 或 SKILL.md）
3. 确保包含完整的文档结构
4. 更新本 README.md 的目录结构
