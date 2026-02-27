# OpenCode 命令 (Commands) 指南

## 概述

自定义命令是可复用的提示模板，通过 `/command-name` 触发。

## 接入方式

### 1. Markdown 文件

```bash
# 项目级
.opencode/commands/my-command.md

# 全局级
~/.config/opencode/commands/my-command.md
```

### 2. JSON 配置

```json
{
  "command": {
    "my-command": {
      "template": "提示内容",
      "description": "命令描述"
    }
  }
}
```

## 功能

### 参数占位符

```markdown
---
description: 创建组件
---

创建一个名为 $ARGUMENTS 的组件。

# 或使用位置参数
创建文件 $1，内容为 $2
```

使用：
```
/component Button
/create-file config.json "content"
```

### Shell 命令

```markdown
---
description: 分析测试
---

测试结果：
!`npm test`

分析以上结果。
```

### 文件引用

```markdown
---
description: 审查文件
---

审查文件 @src/index.ts
```

### 配置选项

```yaml
---
description: 命令描述
agent: build          # 指定代理
model: anthropic/claude-haiku-4-20250514  # 指定模型
subtask: true         # 作为子任务执行
---
```

## 推进过程

### 步骤 1: 创建命令文件

```bash
mkdir -p .opencode/commands
touch .opencode/commands/review.md
```

### 步骤 2: 编写命令

```markdown
---
description: 审查当前更改
agent: plan
---

审查当前的 Git 更改：
!`git diff`

提供改进建议。
```

### 步骤 3: 使用命令

在 OpenCode 中输入：
```
/review
```

## 卡点与解决方案

### 1. 命令不显示

**问题**: 自定义命令没有出现

**解决**: 检查文件位置和 `description` 字段

### 2. Shell 命令失败

**问题**: `!`command`` 执行失败

**解决**: 确保命令在项目根目录可执行

### 3. 参数不替换

**问题**: `$ARGUMENTS` 没有被替换

**解决**: 确保使用正确的语法

## 示例命令

### 运行测试

```markdown
---
description: 运行测试套件
agent: build
---

运行测试并分析结果：
!`npm test 2>&1 || yarn test 2>&1`

对失败的测试提供修复建议。
```

### 项目分析

```markdown
---
description: 分析项目结构
agent: explore
---

分析项目的技术栈和结构。

查看：
- package.json
- README.md
- 配置文件

输出项目概述。
```

### 创建组件

```markdown
---
description: 创建组件 $ARGUMENTS
---

创建组件 $ARGUMENTS：
1. 确定框架（React/Vue/Svelte）
2. 选择合适的位置
3. 创建组件文件
4. 添加类型定义（如适用）
```

### Git 提交

```markdown
---
description: 创建规范的提交
---

基于当前更改创建提交：

!`git status`
!`git diff --staged`

生成符合 Conventional Commits 的提交信息。
```

## 最佳实践

1. **描述清晰**: 在 TUI 中显示
2. **使用代理**: 为命令指定合适的代理
3. **错误处理**: Shell 命令考虑失败情况
4. **参数验证**: 在提示中说明参数要求
