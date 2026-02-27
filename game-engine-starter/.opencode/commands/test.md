---
description: 运行测试
agent: build
---

运行项目的测试套件。

## 执行步骤

1. 检查测试框架（pytest 或 unittest）
2. 运行测试
3. 分析结果

!`pytest tests/ -v --tb=short 2>&1 || python -m pytest tests/ -v 2>&1 || python -m unittest discover tests/ 2>&1`

## 测试分析

如果测试失败：
- 分析失败原因
- 定位问题代码
- 提供修复建议
