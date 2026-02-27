# OpenCode 代理 (Agents) 指南

## 概述

代理是专门的 AI 助手，可以针对特定任务进行优化配置。

## 接入方式

### 1. Markdown 文件

```bash
# 项目级
.opencode/agents/my-agent.md

# 全局级
~/.config/opencode/agents/my-agent.md
```

### 2. JSON 配置

```json
{
  "agent": {
    "my-agent": {
      "description": "代理描述",
      "model": "anthropic/claude-sonnet-4-20250514",
      "prompt": "你是一个专门的助手..."
    }
  }
}
```

## 功能

### 代理类型

| 类型 | 说明 | 使用场景 |
|------|------|----------|
| primary | 主代理，可切换 | 主要对话 |
| subagent | 子代理，可被调用 | 专门任务 |

### 配置选项

```yaml
---
description: 代理描述（必需）
mode: subagent              # primary | subagent
model: anthropic/claude-sonnet-4-20250514
temperature: 0.1
tools:
  write: false
  edit: false
  bash: false
permission:
  bash:
    "git status": allow
    "npm test": allow
hidden: true               # 从自动完成中隐藏
---
```

## 推进过程

### 步骤 1: 创建代理文件

```bash
mkdir -p .opencode/agents
touch .opencode/agents/reviewer.md
```

### 步骤 2: 编写代理定义

```markdown
---
description: 代码审查专家
mode: subagent
tools:
  write: false
  edit: false
---

你是一位代码审查专家，专注于：
- 代码质量
- 安全问题
- 性能优化

请提供建设性的反馈。
```

### 步骤 3: 使用代理

```bash
# 通过 @ 提及
@reviewer 请审查这个文件

# 或者让主代理自动调用
```

## 卡点与解决方案

### 1. 代理不出现

**问题**: 自定义代理没有在列表中显示

**解决**: 检查 `description` 字段是否存在

### 2. 权限问题

**问题**: 代理无法执行某些操作

**解决**: 检查 `tools` 和 `permission` 配置

### 3. 模型不可用

**问题**: 指定的模型不存在

**解决**: 使用正确的模型 ID 格式 `provider/model-id`

## 示例代理

### 代码审查

```markdown
---
description: 代码审查专家
mode: subagent
tools:
  write: false
  edit: false
---

你是一位资深代码审查专家。

## 审查重点
1. 代码质量
2. 安全风险
3. 性能问题

## 输出格式
- 严重问题
- 警告
- 建议
```

### 文档编写

```markdown
---
description: 技术文档编写者
mode: subagent
tools:
  write: true
  bash: false
---

你是一位技术文档专家。

## 写作原则
- 清晰简洁
- 结构化
- 包含示例

## 格式规范
- 使用 Markdown
- 添加代码块
- 使用表格
```

## 最佳实践

1. **单一职责**: 每个代理专注一个领域
2. **清晰描述**: 让模型知道何时调用
3. **权限最小化**: 只给必要的工具权限
4. **温度设置**: 分析任务用低温度，创作任务用高温度
