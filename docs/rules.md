# OpenCode 规则 (Rules) 指南

## 概述

规则通过 `AGENTS.md` 文件为 OpenCode 提供项目特定的上下文和指导。

## 接入方式

### 文件位置

```bash
# 项目级（推荐）
/path/to/project/AGENTS.md

# 全局级
~/.config/opencode/AGENTS.md

# Claude Code 兼容
/path/to/project/CLAUDE.md
~/.claude/CLAUDE.md
```

## 功能

### 1. 项目上下文

```markdown
# 项目名称

项目描述和技术栈说明。

## 项目结构

- `src/` - 源代码
- `tests/` - 测试文件
- `docs/` - 文档

## 技术栈

- 语言: TypeScript
- 框架: React
- 构建: Vite
```

### 2. 编码规范

```markdown
## 代码规范

### 命名约定

- 组件: PascalCase
- 函数: camelCase
- 常量: UPPER_SNAKE_CASE

### 文件组织

- 每个文件一个组件
- 样式与组件同目录
```

### 3. 工作流程

```markdown
## 开发流程

1. 从 develop 创建 feature 分支
2. 编写代码和测试
3. 提交 PR
4. 代码审查后合并

## 提交规范

使用 Conventional Commits
```

### 4. 外部文件引用

通过 `opencode.json` 引用：

```json
{
  "instructions": [
    "docs/guidelines.md",
    "CONTRIBUTING.md",
    ".cursor/rules/*.md"
  ]
}
```

## 推进过程

### 步骤 1: 创建 AGENTS.md

```bash
# 使用 /init 命令自动生成
/init

# 或手动创建
touch AGENTS.md
```

### 步骤 2: 编写内容

```markdown
# My Project

## 技术栈
- React 18
- TypeScript 5
- TailwindCSS

## 代码规范
- 使用函数组件
- 遵循 ESLint 配置

## 测试要求
- 单元测试覆盖率 > 80%
```

### 步骤 3: 提交到 Git

```bash
git add AGENTS.md
git commit -m "docs: add AGENTS.md"
```

## 卡点与解决方案

### 1. 规则不生效

**问题**: AGENTS.md 内容没有被使用

**解决**: 
- 确认文件在项目根目录
- 重启 OpenCode

### 2. 内容过长

**问题**: AGENTS.md 太大，消耗太多 token

**解决**: 
- 使用 `instructions` 引用外部文件
- 保持 AGENTS.md 简洁

### 3. 冲突处理

**问题**: 多个规则文件冲突

**解决**: 
- AGENTS.md 优先于 CLAUDE.md
- 项目级优先于全局

## 示例 AGENTS.md

```markdown
# E-commerce Platform

一个基于 Next.js 的电商平台。

## 项目结构

```
src/
├── app/          # Next.js App Router
├── components/   # React 组件
├── lib/          # 工具函数
├── hooks/        # 自定义 Hooks
└── types/        # TypeScript 类型
```

## 技术栈

- Next.js 14 (App Router)
- TypeScript 5
- TailwindCSS
- Prisma
- PostgreSQL

## 代码规范

### 组件

- 使用函数组件和 Hooks
- 组件文件使用 PascalCase
- 样式使用 TailwindCSS

### API

- RESTful 设计
- 统一错误处理
- 输入验证

### 测试

- 使用 Jest 和 React Testing Library
- 测试文件与源文件同目录
- 覆盖率要求 > 80%

## 工作流程

1. 从 main 创建 feature 分支
2. 开发并测试
3. 创建 Pull Request
4. 通过审查后合并

## 禁止操作

- 不要直接推送到 main
- 不要跳过测试
- 不要忽略 TypeScript 错误
```

## 最佳实践

1. **保持更新**: 随项目变化更新 AGENTS.md
2. **简洁明了**: 只包含必要信息
3. **团队共享**: 提交到 Git 供团队使用
4. **模块化**: 使用 `instructions` 引用详细文档
