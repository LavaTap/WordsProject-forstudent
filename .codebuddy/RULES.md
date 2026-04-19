# CodeBuddy 智能体规则

## 全局规则 - 每次任务必须执行

### 1. Plan 文件管理

**每次调用智能体完成任务时，必须遵守以下规则：**

#### 1.1 创建新 Plan
当用户提出新任务需求时，在 `.codebuddy/plans/` 目录下创建新 Plan 文件：

```
格式: {计划名称}_{时间戳}.md
示例: code-review_2026-04-19_131600.md
      langchain-agent_2026-04-19_140000.md
```

#### 1.2 Plan 文件结构
每个 Plan 必须包含以下部分：

```markdown
---
name: {计划名称}
overview: {一句话概述}
todos:
  - id: task-1
    content: {任务描述}
    status: pending|in_progress|completed
design: {...}
---

## 产品概述
...

## 核心功能
...

## 技术架构
...

## 实现步骤
...

## 注意事项
...
```

#### 1.3 Plan 独立性
- **每个 Plan 独立存在，互不影响**
- 不修改其他 Plan 的内容
- 不引用其他 Plan 的内部状态
- 跨 Plan 协作通过用户传递上下文

### 2. Todo 状态管理

| 状态 | 含义 | 触发时机 |
|------|------|----------|
| `pending` | 待处理 | 创建任务时 |
| `in_progress` | 进行中 | 开始处理时 |
| `completed` | 已完成 | 任务完成时 |
| `blocked` | 被阻塞 | 依赖未完成时 |

### 3. 任务执行流程

```
用户请求 -> 分析需求 -> 创建/更新 Plan -> 执行任务 -> 更新 Todo 状态 -> 报告结果
     ^                                                                 |
     |_________________ 失败时记录问题 ________________________________|
```

### 4. Plan 命名规范

| 类型 | 命名格式 | 示例 |
|------|----------|------|
| 代码审查 | `{feature}_review_{date}` | `app_review_2026-04-19` |
| 功能开发 | `{feature}_dev_{date}` | `login_feature_dev_2026-04-19` |
| Bug修复 | `fix_{bug-name}_{date}` | `fix_login_bug_2026-04-19` |
| 重构 | `refactor_{module}_{date}` | `refactor_auth_2026-04-19` |
| AI集成 | `{feature}_ai_{date}` | `chatbot_ai_2026-04-19` |

### 5. Plan 更新时机

**必须更新 Plan 的场景：**
- ✅ 任务开始执行
- ✅ 某个 Todo 状态变更
- ✅ 发现新的问题或风险
- ✅ 任务完成
- ✅ 用户需求变更

**禁止行为：**
- ❌ 不更新 Plan 就完成任务
- ❌ 修改其他 Plan 的内容
- ❌ 删除未完成的 Plan
- ❌ 合并多个独立 Plan

## 目录结构

```
.codebuddy/
├── RULES.md           # 本规则文件
├── README.md          # 架构说明
├── agents/            # 智能体定义
│   └── {agent-name}/
│       └── agent.md   # 智能体详细定义
├── plans/             # 任务计划（每个任务一个文件）
│   └── {name}_{date}.md
├── skills/            # 技能定义
│   └── {skill-name}/
│       └── SKILL.md
└── teams/             # 团队协作记录
    └── {team-name}/
```

## 快速参考

**创建新 Plan：**
```markdown
---
name: new-feature-dev
overview: 开发新功能
todos:
  - id: step-1
    content: 步骤1
    status: pending
---
```

**更新 Todo：**
```markdown
todos:
  - id: step-1
    content: 步骤1
    status: completed  # 或 in_progress
```

**报告格式：**
```
✅ 已完成: [任务名称]
📋 当前进度: X/Y
📁 Plan 位置: .codebuddy/plans/{name}_{date}.md
```
