---
description: 生成 Socket 测试代码模板
agent: build
---

为游戏生成 Socket 测试框架代码。

## 生成内容

### 1. 游戏端 Socket 服务器

```python
# src/engine/testing/socket_server.py
```

### 2. 测试客户端

```python
# tests/e2e/client.py
```

### 3. 测试启动器

```python
# tests/e2e/launcher.py
```

### 4. 测试配置

```python
# tests/e2e/conftest.py
```

## 集成步骤

1. 将生成的代码放入相应目录
2. 在游戏入口添加 `--test-mode` 参数支持
3. 实现 `GameTestServer` 需要的方法
4. 运行 `/e2e` 命令测试

## 自定义

根据游戏的具体实现，需要自定义：
- 实体创建逻辑
- 组件访问方式
- 状态管理接口
- 输入处理方式
