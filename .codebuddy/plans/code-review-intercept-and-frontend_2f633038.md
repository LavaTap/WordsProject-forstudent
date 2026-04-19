---
name: code-review-intercept-and-frontend
overview: 改造代码评审平台：Webhook 接收 GitHub push/PR 时拦截并返回"已触发评审"（不直接调用AI），新增待评审列表接口供前端展示，创建简易前端页面（含"触发AI评审"按钮），新增手动触发AI评审接口，评审通过则允许合并、有强制问题则禁止合并。同时新建 good_example_A.py 测试脚本和对应的拦截测试脚本。
status: migrated  # 原为 Code-repository-review 项目，已迁移至 WordsProject-forstudent
migrated_date: 2026-04-19
original_project: Code-repository-review
current_project: WordsProject-forstudent
design:
  architecture:
    framework: html
  styleKeywords:
    - Dark Tech
    - Cyberpunk Dark Mode
    - Cyan Accent
    - Card-based Layout
    - Micro-interactions
    - Developer Tool Aesthetic
  fontSystem:
    fontFamily: JetBrains Mono, monospace
    heading:
      size: 24px
      weight: 700
    subheading:
      size: 16px
      weight: 600
    body:
      size: 14px
      weight: 400
  colorSystem:
    primary:
      - "#00D4FF"
      - "#0EA5E9"
      - "#06B6D4"
    background:
      - "#0D1117"
      - "#161B22"
      - "#1C2333"
    text:
      - "#E6EDF3"
      - "#8B949E"
      - "#58A6FF"
    functional:
      - "#3FB950"
      - "#F85149"
      - "#D29922"
todos:
  - id: modify-models-db
    content: 修改 models.py 的 Review 模型添加 source_type/repo_name/pr_number 字段，处理 SQLite 列新增
    status: completed
  - id: refactor-webhook-intercept
    content: 重构 webhook.py 将 _perform_review 替换为 _intercept_and_save，返回"已触发评审"
    status: completed
    dependencies:
      - modify-models-db
  - id: extend-review-routes
    content: 扩展 review.py 新增 GET /api/review/pending 和 POST /api/review/<id>/trigger 接口
    status: completed
    dependencies:
      - modify-models-db
  - id: update-app-routes
    content: 修改 app.py 注册静态文件目录路由和 dashboard 页面路由
    status: completed
    dependencies:
      - extend-review-routes
  - id: create-good-example
    content: 新建 good_example_A.py 约20行规范 Python 好代码示例
    status: completed
  - id: create-test-script
    content: 编写 test_intercept_review.py 测试拦截+触发AI评审完整流程
    status: completed
    dependencies:
      - refactor-webhook-intercept
      - extend-review-routes
  - id: create-frontend-page
    content: 创建 static/index.html 简易前端页面含待评审列表和触发按钮
    status: completed
    dependencies:
      - update-app-routes
      - extend-review-routes
  - id: e2e-test
    content: 使用 [playwright-cli] 进行端到端测试验证完整流程
    status: completed
    dependencies:
      - create-test-script
      - create-frontend-page
---

## 产品概述

搭建一个代码评审拦截平台，当代码被推送到 GitHub 仓库（https://github.com/LavaTap/Code-repository-review-system）时，系统通过 Webhook **拦截**代码，**不直接触发AI评审**，而是返回"已触发评审"信息，在前端页面展示待评审记录。用户手动点击"触发AI评审"按钮后，才将代码发送给 AI 审查。审查通过则允许合并，审查失败（有强制问题）则显示"禁止"，阻止合并。

## 核心功能

- **Webhook 拦截改造**: GitHub PR/Push 事件到达时，不再直接调用 AI 审查，而是创建 `pending` 状态的 Review 记录并返回 `{message: "已触发评审", review_id: N}`
- **待评审列表接口**: 新增 `GET /api/review/pending` 接口，返回所有 pending 状态的评审记录供前端展示
- **手动触发 AI 评审接口**: 新增 `POST /api/review/<id>/trigger` 接口，前端点击按钮后调用此接口执行 AI 审查，更新状态为 passed/failed，返回 merge_allowed 和审查结果
- **good_example_A.py**: 创建约20行的规范 Python 好代码示例文件
- **测试脚本 test_intercept_review.py**: 测试 good_example_A 上传后被拦截的完整流程（模拟 Webhook -> 拦截 -> 返回"已触发评审" -> 触发AI评审 -> 结果判断）
- **简易前端页面**: 在 Flask static 目录下提供单页 HTML，展示待评审列表 + "触发AI评审"按钮，点击后显示评审结果（通过/禁止合并）

## 技术栈

- 后端框架: Flask (现有)
- 数据库: SQLite + SQLAlchemy (现有)
- LLM: LangChain + DeepSeek V3 (现有)
- 前端: 纯 HTML + JavaScript（内嵌在 Flask static 中，无需额外构建工具）
- 测试脚本: Python requests

## 技术架构

### 系统架构变更（核心改动）

当前流程:

```
GitHub PR/Push -> Webhook -> 验证用户 -> 直接调AI审查 -> 返回 passed/failed -> 合并/拒绝
```

目标流程:

```
GitHub PR/Push -> Webhook -> 验证用户 -> [拦截]创建pending记录 -> 返回"已触发评审"
                                                          |
                                                          v
前端页面显示待评审列表 -> 用户点击"触发AI评审"按钮 -> POST /api/review/<id>/trigger
                                                          |
                                                          v
                                              调用AI审查 -> 更新review状态
                                                          |
                                          +---------------+---------------+
                                          |                               |
                                  has_mandatory=true              has_mandatory=false
                                  status=failed                   status=passed
                                  "禁止合并"                       "允许合并"
```

### 关键实现策略

1. **webhook.py 改造**: `_handle_pull_request` 和 `_handle_push` 不再调用 `_perform_review()`，改为调用新函数 `_intercept_and_save()`，该函数仅保存 Review 记录（status=pending），返回 `{status: "intercepted", message: "已触发评审", review_id: N}`
2. **review.py 扩展**: 

- `GET /api/review/pending` - 查询 status='pending' 的记录
- `POST /api/review/<id>/trigger` - 根据 review_id 查出 code_content，调用 agent.review()，更新 Review 记录的 result_json、has_mandatory_issues、status 字段

3. **models.py 扩展**: Review 模型新增 `source_type`(pull_request/push)、`repo_name`(仓库全名)、`pr_number`(PR编号) 字段，用于记录来源信息
4. **app.py 改造**: 添加 `static` 文件件路由和首页路由 `/dashboard` 提供前端页面

### 目录结构

```
d:\code\private\WordsProject-forstudent\    # 当前项目（已从 Code-repository-review 迁移）
├── app.py                                 # [MODIFY] 注册static目录路由 + /dashboard页面路由
├── models.py                              # [MODIFY] Review模型增加source_type, repo_name, pr_number字段
├── db_init.py                             # [无修改] 数据库初始化
├── routers/
│   ├── auth.py                            # [无修改] 用户认证
│   ├── webhook.py                         # [NEW] Webhook接收GitHub事件
│   └── review.py                          # [NEW] 评审接口（/pending, /<id>/trigger）
├── agents/
│   └── code_review_agent.py               # [已有] AI代码审查智能体
├── good_example_A.py                      # [NEW] 约20行规范Python好代码
├── test_intercept_review.py               # [NEW] 测试完整拦截+评审流程
├── static/
│   └── index.html                         # [NEW] 简易前端页面: 待评审列表+触发按钮+结果显示
└── templates/
    └── dashboard.html                     # [NEW] 评审仪表板页面
```

### 实施状态

| 任务 | 状态 | 说明 |
|------|------|------|
| modify-models-db | ✅ completed | 原项目已完成 |
| refactor-webhook-intercept | ✅ completed | 原项目已完成 |
| extend-review-routes | ✅ completed | 原项目已完成 |
| update-app-routes | ✅ completed | 原项目已完成 |
| create-good-example | ✅ completed | 原项目已完成 |
| create-test-script | ✅ completed | 原项目已完成 |
| create-frontend-page | ✅ completed | 原项目已完成 |
| e2e-test | ✅ completed | 原项目已完成 |

### 实现注意事项

- **SQLite ALTER TABLE**: 新增列需要使用 ALTER TABLE ADD COLUMN 或直接删库重建（开发阶段推荐后者）
- **Webhook 签名验证保持不变**: 拦截逻辑不影响现有的安全校验链路
- **_perform_review 函数保留**: trigger 接口内部复用该函数的 AI 调用逻辑，避免重复代码
- **前端页面极简设计**: 单个 HTML 文件内嵌 CSS/JS，Flask `send_from_directory` 或直接提供路由渲染

## 设计风格与架构

采用 **深色科技风 (Cyberpunk Dark Tech)** 设计语言，契合"代码评审平台"的技术属性。整体为暗色背景搭配青色(cyan)高亮色，营造专业开发者工具氛围。

### 页面规划：单一仪表板页面 (`static/index.html`)

#### Block 1 - 顶部导航栏

固定顶部导航条，左侧显示平台名称"Code Repository Review System"，右侧显示连接状态指示灯（绿=已连接/红=断开）。深灰底色配青色文字。

#### Block 2 - 待评审队列区域

页面核心区域，卡片式布局展示所有 pending 状态的评审记录。每张卡片包含：

- 文件名（高亮显示）
- 来源信息（PR #xx / Push to branch）
- 提交者用户名
- 触发时间
- 右侧醒目的"触发 AI 评审"按钮（青色渐变，hover 有发光效果）

#### Block 3 - 评审结果展示区

初始隐藏，点击"触发AI评审"后在此区域动态加载结果：

- 通过场景：绿色边框卡片 + "评审通过"徽章 + "允许合并"提示 + 审查详情折叠面板
- 失败场景：红色边框卡片 + "**禁止合并**" 大字警告（红色加粗闪烁）+ 强制问题列表

#### Block 4 - 底部信息栏

显示版本号和 API 状态，简洁一行即可。

### 交互设计

- 按钮 hover 时有微妙的上浮阴影效果 + 边框发光
- 触发AI评审后按钮变为 loading 状态（转圈动画），禁用重复点击
- 结果出现时有淡入动画（CSS transition opacity 0.3s）
- "禁止"文字使用红色脉冲动画吸引注意

## Agent Extensions

- **playwright-cli**
- Purpose: 自动化浏览器操作来测试前端页面的完整交互流程（打开页面、查看待评审列表、点击触发AI评审按钮、验证结果显示）
- Expected outcome: 自动化端到端测试报告，确认从拦截到评审结果展示的全链路正常工作