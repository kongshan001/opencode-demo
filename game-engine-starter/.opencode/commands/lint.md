---
description: 代码质量检查
agent: plan
---

运行代码质量检查工具。

## 检查项目

### 1. 代码格式检查

!`black --check src/ 2>&1 || echo "Black not installed"`

### 2. 导入排序检查

!`isort --check-only src/ 2>&1 || echo "isort not installed"`

### 3. 类型检查

!`mypy src/ --ignore-missing-imports 2>&1 || echo "mypy not installed"`

### 4. 代码规范检查

!`pylint src/ --disable=C0114,C0115,C0116 2>&1 || echo "pylint not installed"`

## 分析结果

根据检查结果：
- 列出需要修复的问题
- 按严重程度排序
- 提供修复建议
