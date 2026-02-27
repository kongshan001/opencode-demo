---
name: git-workflow
description: Git 工作流助手，处理分支、提交、合并等操作
license: MIT
compatibility: opencode
metadata:
  category: version-control
  audience: developers
---

## Git 工作流技能

处理 Git 相关的操作和工作流。

## 使用场景

- 创建功能分支
- 编写规范的提交信息
- 处理合并冲突
- 发布版本管理

## 提交信息规范

遵循 Conventional Commits 规范：

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### 类型 (type)

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档变更
- `style`: 代码格式（不影响逻辑）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具相关

## 分支策略

- `main`: 生产分支
- `develop`: 开发分支
- `feature/*`: 功能分支
- `hotfix/*`: 紧急修复分支

## 注意事项

- 提交前检查代码格式
- 确保测试通过
- 避免直接提交到 main 分支
