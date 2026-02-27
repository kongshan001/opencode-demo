# 测试目录结构

```
tests/
├── conftest.py           # 共享 fixtures 和 Mock
├── unit/                 # 单元测试
│   ├── test_vector.py
│   ├── test_entity.py
│   ├── test_component.py
│   └── test_object_pool.py
├── integration/          # 集成测试
│   ├── test_systems.py
│   ├── test_collision.py
│   └── test_rendering.py
├── benchmark/            # 性能基准测试
│   ├── conftest.py
│   └── test_core_performance.py
└── stress/               # 压力测试
    └── test_load.py
```

## 运行测试

```bash
# 运行所有测试
pytest

# 只运行单元测试
pytest tests/unit -v

# 只运行集成测试
pytest tests/integration -v

# 运行基准测试
pytest tests/benchmark --benchmark-only

# 运行压力测试
pytest tests/stress -v -s

# 生成覆盖率报告
pytest --cov=src --cov-report=html

# 并行测试
pytest -n auto
```

## Mock 架构

所有 Mock 组件在 `conftest.py` 中定义：

- `MockRenderer` - 模拟渲染器
- `MockWindow` - 模拟窗口
- `MockAudio` - 模拟音频
- `MockAssetLoader` - 模拟资源加载
- `TestEngineContext` - 测试用引擎上下文

## 性能基线

| 测试项 | 基线 |
|--------|------|
| 实体创建 (1000个) | < 100ms |
| 实体更新 (1000个) | < 1ms |
| 向量运算 | < 0.01ms |
| 碰撞检测 | < 0.5ms |
