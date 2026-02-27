# OpenCode 技能 (Skills) 指南

## 概述

技能是可复用的行为定义，按需加载，用于指导模型的行为。

## 接入方式

### 文件位置

```bash
# 项目级
.opencode/skills/my-skill/SKILL.md

# 全局级
~/.config/opencode/skills/my-skill/SKILL.md

# Claude Code 兼容
.claude/skills/my-skill/SKILL.md
```

## 功能

### Frontmatter 字段

```yaml
---
name: skill-name           # 必需，1-64字符
description: 技能描述       # 必需，1-1024字符
license: MIT               # 可选
compatibility: opencode    # 可选
metadata:                  # 可选
  category: quality
  audience: developers
---
```

### 名称规则

- 小写字母和数字
- 单个连字符分隔
- 不能以连字符开头或结尾
- 不能有连续连字符

正则: `^[a-z0-9]+(-[a-z0-9]+)*$`

## 推进过程

### 步骤 1: 创建目录

```bash
mkdir -p .opencode/skills/my-skill
```

### 步骤 2: 创建 SKILL.md

```markdown
---
name: my-skill
description: 技能描述
---

## 功能说明

详细描述这个技能做什么。

## 使用场景

- 场景 1
- 场景 2

## 执行步骤

1. 第一步
2. 第二步
```

### 步骤 3: 使用技能

模型会自动发现并按需加载技能。

## 卡点与解决方案

### 1. 技能不显示

**问题**: 技能没有出现在可用列表

**解决**:
- 确认文件名是 `SKILL.md`（大写）
- 检查 frontmatter 格式
- 验证 name 和 description 字段

### 2. 名称冲突

**问题**: 多个同名技能

**解决**: OpenCode 使用第一个找到的，确保名称唯一

### 3. 权限问题

**问题**: 技能被拒绝访问

**解决**: 检查 `permission.skill` 配置

## 示例技能

### 代码审查

```markdown
---
name: code-review
description: 执行代码审查
---

## 审查流程

1. 收集上下文
2. 静态分析
3. 深度审查
4. 输出报告

## 审查重点

- 代码质量
- 安全风险
- 性能问题
```

### Git 工作流

```markdown
---
name: git-workflow
description: Git 操作指南
---

## 提交规范

使用 Conventional Commits:
- feat: 新功能
- fix: 修复
- docs: 文档

## 分支策略

- main: 生产
- develop: 开发
- feature/*: 功能
```

## 权限配置

```json
{
  "permission": {
    "skill": {
      "*": "allow",
      "internal-*": "deny",
      "experimental-*": "ask"
    }
  }
}
```

## 最佳实践

1. **描述精准**: 让模型能正确判断何时使用
2. **内容简洁**: 只包含必要信息
3. **结构清晰**: 使用 Markdown 格式化
4. **按需加载**: 技能只在需要时加载
