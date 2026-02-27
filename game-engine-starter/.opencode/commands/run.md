---
description: 运行游戏
agent: build
---

启动游戏进行测试运行。

## 执行步骤

1. 检查主入口文件（main.py 或 game.py）
2. 运行游戏
3. 监控启动日志

!`python main.py 2>&1 || python game.py 2>&1 || python src/main.py 2>&1`

如果启动失败，请分析错误并提供解决方案。
