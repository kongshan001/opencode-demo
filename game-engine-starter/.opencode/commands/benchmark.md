---
description: 运行基准测试
agent: build
---

运行性能基准测试并分析结果。

## 测试内容

### 核心性能测试

!`pytest tests/benchmark -v --benchmark-only --benchmark-sort=mean 2>&1`

### 分析结果

1. 识别性能瓶颈
2. 对比历史基线
3. 提供优化建议

## 输出格式

```markdown
## 基准测试报告

### 通过的测试
- [测试名]: XX ms (基线: XX ms)

### 超出基线的测试
- [测试名]: XX ms (超出 XX%)

### 优化建议
- [具体建议]
```
