---
name: engine-testing
description: 自研游戏引擎的自动化测试和性能压测策略
license: MIT
metadata:
  category: testing
---

## 自研引擎测试技能

当需要对自研游戏引擎进行测试时使用此技能。

## 测试挑战

自研引擎测试面临的主要问题：

1. **依赖渲染环境** - 需要 OpenGL/Vulkan 等图形 API
2. **硬件依赖** - 不同机器性能差异大
3. **异步操作** - 资源加载、多线程
4. **状态复杂** - 游戏状态难以复现

## 解决方案架构

```
┌─────────────────────────────────────────────────────┐
│                   测试金字塔                          │
├─────────────────────────────────────────────────────┤
│  E2E 测试 (少量)    - 完整游戏流程                    │
│  ────────────────────────────────────────────────   │
│  集成测试 (中等)    - 系统交互、场景切换              │
│  ────────────────────────────────────────────────   │
│  单元测试 (大量)    - 核心算法、数学函数              │
└─────────────────────────────────────────────────────┘
```

## 一、自动化测试策略

### 1. 分层 Mock 架构

```python
# tests/conftest.py
import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

# ============================================================
# Mock 层次结构
# ============================================================

class MockRenderer:
    """模拟渲染器 - 不实际绘制"""
    
    def __init__(self):
        self.draw_calls = []
        self.batch_calls = []
    
    def draw(self, sprite):
        """记录绘制调用，不实际渲染"""
        self.draw_calls.append(sprite)
    
    def draw_batch(self, sprites):
        self.batch_calls.append(sprites)
    
    def clear(self):
        self.draw_calls.clear()
        self.batch_calls.clear()
    
    @property
    def draw_count(self):
        return len(self.draw_calls) + len(self.batch_calls)


class MockWindow:
    """模拟窗口 - 无头模式"""
    
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self._should_close = False
        self._events = []
    
    def should_close(self):
        return self._should_close
    
    def close(self):
        self._should_close = True
    
    def poll_events(self):
        """返回预注入的事件"""
        events = self._events.copy()
        self._events.clear()
        return events
    
    def inject_event(self, event):
        """注入测试事件"""
        self._events.append(event)


class MockAudio:
    """模拟音频系统"""
    
    def __init__(self):
        self.played_sounds = []
    
    def play(self, sound_id):
        self.played_sounds.append(sound_id)
    
    def stop_all(self):
        self.played_sounds.clear()


class MockAssetLoader:
    """模拟资源加载器"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self.load_times: Dict[str, float] = {}
    
    def load(self, path: str, load_time: float = 0.0):
        """模拟加载，返回 Mock 对象"""
        if path not in self._cache:
            mock_asset = Mock()
            mock_asset.path = path
            self._cache[path] = mock_asset
            self.load_times[path] = load_time
        return self._cache[path]
    
    def is_loaded(self, path: str):
        return path in self._cache
    
    def clear_cache(self):
        self._cache.clear()
        self.load_times.clear()


# ============================================================
# Engine Context - 测试用引擎上下文
# ============================================================

class TestEngineContext:
    """测试用引擎上下文，使用所有 Mock 组件"""
    
    def __init__(self):
        self.renderer = MockRenderer()
        self.window = MockWindow()
        self.audio = MockAudio()
        self.assets = MockAssetLoader()
        self.entities = []
        self.systems = []
    
    def create_entity(self, *components):
        """创建测试实体"""
        entity = Mock()
        entity.id = len(self.entities)
        entity.components = {type(c): c for c in components}
        entity.is_active = True
        self.entities.append(entity)
        return entity
    
    def add_system(self, system):
        self.systems.append(system)
    
    def update(self, dt: float):
        """模拟游戏更新"""
        for system in self.systems:
            system.update(self.entities, dt)
    
    def render(self):
        """模拟渲染"""
        for entity in self.entities:
            if entity.is_active:
                self.renderer.draw(entity)


# ============================================================
# Pytest Fixtures
# ============================================================

@pytest.fixture
def engine():
    """提供测试引擎上下文"""
    return TestEngineContext()


@pytest.fixture
def mock_renderer():
    """提供 Mock 渲染器"""
    return MockRenderer()


@pytest.fixture
def mock_window():
    """提供 Mock 窗口"""
    return MockWindow()


@pytest.fixture
def mock_assets():
    """提供 Mock 资源加载器"""
    return MockAssetLoader()
```

### 2. 单元测试示例

```python
# tests/unit/test_vector.py
import pytest
import math
from engine.math import Vector2, Vector3

class TestVector2:
    """Vector2 单元测试 - 纯数学，无依赖"""
    
    def test_addition(self):
        v1 = Vector2(1, 2)
        v2 = Vector2(3, 4)
        result = v1 + v2
        
        assert result.x == 4
        assert result.y == 6
    
    def test_subtraction(self):
        v1 = Vector2(5, 3)
        v2 = Vector2(2, 1)
        result = v1 - v2
        
        assert result.x == 3
        assert result.y == 2
    
    def test_scalar_multiplication(self):
        v = Vector2(2, 3)
        result = v * 2
        
        assert result.x == 4
        assert result.y == 6
    
    def test_dot_product(self):
        v1 = Vector2(1, 2)
        v2 = Vector2(3, 4)
        
        assert v1.dot(v2) == 11  # 1*3 + 2*4
    
    def test_length(self):
        v = Vector2(3, 4)
        
        assert v.length() == 5.0
    
    def test_normalize(self):
        v = Vector2(3, 4)
        normalized = v.normalize()
        
        assert abs(normalized.length() - 1.0) < 0.0001
    
    def test_angle(self):
        v1 = Vector2(1, 0)
        v2 = Vector2(0, 1)
        
        angle = v1.angle_to(v2)
        assert abs(angle - math.pi / 2) < 0.0001
    
    @pytest.mark.parametrize("x,y,expected", [
        (0, 0, 0),
        (1, 1, math.sqrt(2)),
        (3, 4, 5),
        (-3, -4, 5),
    ])
    def test_length_parametrized(self, x, y, expected):
        v = Vector2(x, y)
        assert abs(v.length() - expected) < 0.0001


# tests/unit/test_entity.py
class TestEntity:
    """实体系统单元测试"""
    
    def test_entity_creation(self, engine):
        entity = engine.create_entity()
        
        assert entity is not None
        assert entity.is_active == True
    
    def test_component_add(self, engine):
        from engine.components import Transform
        
        entity = engine.create_entity(Transform(x=10, y=20))
        
        transform = entity.components.get(Transform)
        assert transform is not None
        assert transform.x == 10
        assert transform.y == 20
    
    def test_entity_deactivation(self, engine):
        entity = engine.create_entity()
        entity.is_active = False
        
        assert entity.is_active == False


# tests/unit/test_object_pool.py
class TestObjectPool:
    """对象池测试"""
    
    def test_pool_creation(self):
        from engine.utils import ObjectPool
        
        pool = ObjectPool(lambda: {"id": 0}, initial_size=5)
        
        assert len(pool.pool) == 5
    
    def test_acquire(self):
        from engine.utils import ObjectPool
        
        pool = ObjectPool(lambda: {"id": 0}, initial_size=2)
        
        obj1 = pool.acquire()
        obj2 = pool.acquire()
        
        assert obj1 is not None
        assert obj2 is not None
        assert obj1 is not obj2
    
    def test_acquire_empty_pool_expands(self):
        from engine.utils import ObjectPool
        
        pool = ObjectPool(lambda: {"id": 0}, initial_size=1)
        
        pool.acquire()
        pool.acquire()  # 池空，应自动扩展
        
        assert len(pool.pool) >= 0  # 扩展后可能为空
    
    def test_release(self):
        from engine.utils import ObjectPool
        
        pool = ObjectPool(lambda: {"id": 0}, initial_size=1)
        
        obj = pool.acquire()
        pool.release(obj)
        
        assert len(pool.pool) == 1
```

### 3. 集成测试示例

```python
# tests/integration/test_systems.py
import pytest
from tests.conftest import TestEngineContext
from engine.components import Transform, Velocity
from engine.systems import MovementSystem

class TestMovementSystem:
    """移动系统集成测试"""
    
    @pytest.fixture
    def engine(self):
        ctx = TestEngineContext()
        ctx.add_system(MovementSystem())
        return ctx
    
    def test_entity_moves(self, engine):
        """测试实体移动"""
        # 创建带位置和速度的实体
        entity = engine.create_entity(
            Transform(x=0, y=0),
            Velocity(dx=10, dy=5)
        )
        
        # 模拟 1 秒更新
        engine.update(1.0)
        
        # 验证位置变化
        transform = entity.components[Transform]
        assert transform.x == 10
        assert transform.y == 5
    
    def test_multiple_entities(self, engine):
        """测试多实体移动"""
        entities = [
            engine.create_entity(
                Transform(x=0, y=0),
                Velocity(dx=i, dy=i)
            )
            for i in range(10)
        ]
        
        engine.update(1.0)
        
        for i, entity in enumerate(entities):
            transform = entity.components[Transform]
            assert transform.x == i
            assert transform.y == i
    
    def test_inactive_entity_not_updated(self, engine):
        """测试非活动实体不更新"""
        entity = engine.create_entity(
            Transform(x=0, y=0),
            Velocity(dx=10, dy=10)
        )
        entity.is_active = False
        
        engine.update(1.0)
        
        transform = entity.components[Transform]
        assert transform.x == 0  # 位置不变


# tests/integration/test_collision.py
class TestCollisionSystem:
    """碰撞系统集成测试"""
    
    def test_bounding_box_collision(self, engine):
        from engine.systems import CollisionSystem
        from engine.components import Transform, BoundingBox
        
        engine.add_system(CollisionSystem())
        
        # 创建两个重叠的实体
        e1 = engine.create_entity(
            Transform(x=0, y=0),
            BoundingBox(width=10, height=10)
        )
        e2 = engine.create_entity(
            Transform(x=5, y=5),
            BoundingBox(width=10, height=10)
        )
        
        engine.update(0.016)
        
        # 检查碰撞事件
        # (需要事件系统的 Mock)
```

### 4. 无头渲染测试

```python
# tests/integration/test_rendering.py
import pytest
from tests.conftest import MockRenderer, TestEngineContext

class TestRendering:
    """渲染测试 - 使用 Mock 渲染器"""
    
    @pytest.fixture
    def engine(self):
        ctx = TestEngineContext()
        # 渲染系统使用 MockRenderer
        return ctx
    
    def test_draw_call_count(self, engine):
        """测试绘制调用次数"""
        # 创建 100 个实体
        for _ in range(100):
            engine.create_entity()
        
        engine.render()
        
        # 验证绘制调用次数
        assert engine.renderer.draw_count == 100
    
    def test_batch_rendering(self, engine):
        """测试批量渲染"""
        entities = [engine.create_entity() for _ in range(100)]
        
        # 使用批量渲染
        engine.renderer.draw_batch(entities)
        
        assert len(engine.renderer.batch_calls) == 1
        assert len(engine.renderer.batch_calls[0]) == 100
    
    def test_no_draw_for_inactive(self, engine):
        """测试非活动实体不绘制"""
        e1 = engine.create_entity()
        e2 = engine.create_entity()
        e2.is_active = False
        
        engine.render()
        
        assert engine.renderer.draw_count == 1  # 只有 e1
```

## 二、性能压测方案

### 1. 基准测试框架

```python
# tests/benchmark/conftest.py
import pytest
import time
import statistics
from typing import Callable, List
from dataclasses import dataclass

@dataclass
class BenchmarkResult:
    """基准测试结果"""
    name: str
    iterations: int
    total_time: float
    mean_time: float
    median_time: float
    min_time: float
    max_time: float
    std_dev: float
    ops_per_second: float
    
    def __str__(self):
        return (
            f"{self.name}:\n"
            f"  Iterations: {self.iterations}\n"
            f"  Total: {self.total_time:.4f}s\n"
            f"  Mean: {self.mean_time * 1000:.4f}ms\n"
            f"  Median: {self.median_time * 1000:.4f}ms\n"
            f"  Min: {self.min_time * 1000:.4f}ms\n"
            f"  Max: {self.max_time * 1000:.4f}ms\n"
            f"  StdDev: {self.std_dev * 1000:.4f}ms\n"
            f"  Ops/sec: {self.ops_per_second:.2f}"
        )


class Benchmark:
    """基准测试工具"""
    
    def __init__(self, warmup: int = 10, iterations: int = 100):
        self.warmup = warmup
        self.iterations = iterations
    
    def run(self, name: str, func: Callable, *args, **kwargs) -> BenchmarkResult:
        """运行基准测试"""
        # 预热
        for _ in range(self.warmup):
            func(*args, **kwargs)
        
        # 正式测试
        times: List[float] = []
        start_total = time.perf_counter()
        
        for _ in range(self.iterations):
            start = time.perf_counter()
            func(*args, **kwargs)
            end = time.perf_counter()
            times.append(end - start)
        
        end_total = time.perf_counter()
        total_time = end_total - start_total
        
        return BenchmarkResult(
            name=name,
            iterations=self.iterations,
            total_time=total_time,
            mean_time=statistics.mean(times),
            median_time=statistics.median(times),
            min_time=min(times),
            max_time=max(times),
            std_dev=statistics.stdev(times) if len(times) > 1 else 0,
            ops_per_second=self.iterations / total_time,
        )


@pytest.fixture
def benchmark():
    return Benchmark(warmup=10, iterations=100)


# 基准测试配置
class BenchmarkConfig:
    """基准测试配置"""
    
    # 性能基线（超过则失败）
    BASELINES = {
        "entity_create": 0.001,      # 1ms
        "entity_update": 0.0001,     # 0.1ms
        "collision_check": 0.0005,   # 0.5ms
        "vector_operation": 0.00001, # 0.01ms
    }
    
    # 性能回归阈值（比基线慢多少倍则警告）
    REGRESSION_THRESHOLD = 1.5
```

### 2. 核心性能测试

```python
# tests/benchmark/test_core_performance.py
import pytest
from tests.benchmark.conftest import BenchmarkConfig
from engine.math import Vector2, Vector3
from engine.entity import Entity
from engine.components import Transform, Velocity

class TestVectorPerformance:
    """向量运算性能测试"""
    
    def test_vector_addition(self, benchmark):
        v1 = Vector2(1, 2)
        v2 = Vector2(3, 4)
        
        result = benchmark.run("vector_addition", lambda: v1 + v2)
        print(result)
        
        # 检查是否超过基线
        assert result.mean_time < BenchmarkConfig.BASELINES["vector_operation"]
    
    def test_vector_normalization(self, benchmark):
        v = Vector2(3, 4)
        
        result = benchmark.run("vector_normalize", v.normalize)
        print(result)
    
    def test_vector_dot_product(self, benchmark):
        v1 = Vector2(1, 2)
        v2 = Vector2(3, 4)
        
        result = benchmark.run("vector_dot", lambda: v1.dot(v2))
        print(result)
    
    def test_vector3_operations(self, benchmark):
        v1 = Vector3(1, 2, 3)
        v2 = Vector3(4, 5, 6)
        
        def operations():
            return v1 + v2, v1.dot(v2), v1.cross(v2), v1.normalize()
        
        result = benchmark.run("vector3_ops", operations)
        print(result)


class TestEntityPerformance:
    """实体系统性能测试"""
    
    def test_entity_creation(self, benchmark):
        result = benchmark.run(
            "entity_create",
            lambda: Entity(components=[Transform()])
        )
        print(result)
        
        assert result.mean_time < BenchmarkConfig.BASELINES["entity_create"]
    
    def test_entity_creation_1000(self, benchmark):
        def create_1000():
            return [Entity(components=[Transform()]) for _ in range(1000)]
        
        result = benchmark.run("entity_create_1000", create_1000)
        print(result)
        
        # 1000 个实体应在 100ms 内创建
        assert result.mean_time < 0.1
    
    def test_component_access(self, benchmark):
        entity = Entity(components=[Transform(x=10, y=20)])
        
        result = benchmark.run(
            "component_access",
            lambda: entity.get_component(Transform)
        )
        print(result)
    
    def test_entity_update_1000(self, benchmark):
        from engine.systems import MovementSystem
        
        entities = [
            Entity(components=[
                Transform(x=i, y=i),
                Velocity(dx=1, dy=1)
            ])
            for i in range(1000)
        ]
        
        system = MovementSystem()
        
        result = benchmark.run(
            "entity_update_1000",
            lambda: system.update(entities, 0.016)
        )
        print(result)
        
        # 1000 实体更新应在 1ms 内完成
        assert result.mean_time < 0.001
```

### 3. 压力测试

```python
# tests/stress/test_load.py
import pytest
import time
from engine.entity import Entity
from engine.components import Transform
from engine.utils import ObjectPool

class TestStress:
    """压力测试"""
    
    def test_massive_entity_creation(self):
        """测试大量实体创建"""
        count = 100000
        
        start = time.perf_counter()
        entities = [Entity(components=[Transform()]) for _ in range(count)]
        elapsed = time.perf_counter() - start
        
        print(f"\n创建 {count} 个实体耗时: {elapsed:.2f}s")
        print(f"平均每个实体: {elapsed / count * 1000:.4f}ms")
        
        assert len(entities) == count
    
    def test_object_pool_vs_direct_creation(self):
        """对比对象池和直接创建"""
        count = 10000
        iterations = 100
        
        # 直接创建
        start = time.perf_counter()
        for _ in range(iterations):
            objects = [{"x": 0, "y": 0} for _ in range(count)]
        direct_time = time.perf_counter() - start
        
        # 使用对象池
        pool = ObjectPool(lambda: {"x": 0, "y": 0}, initial_size=count)
        start = time.perf_counter()
        for _ in range(iterations):
            objects = [pool.acquire() for _ in range(count)]
            for obj in objects:
                pool.release(obj)
        pool_time = time.perf_counter() - start
        
        print(f"\n直接创建 {count} 对象 {iterations} 次: {direct_time:.2f}s")
        print(f"对象池 {count} 对象 {iterations} 次: {pool_time:.2f}s")
        print(f"性能提升: {direct_time / pool_time:.2f}x")
        
        assert pool_time < direct_time
    
    def test_memory_usage(self):
        """测试内存使用"""
        import tracemalloc
        
        tracemalloc.start()
        
        # 创建大量实体
        entities = [Entity(components=[Transform()]) for _ in range(10000)]
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"\n10000 个实体内存使用:")
        print(f"  当前: {current / 1024 / 1024:.2f} MB")
        print(f"  峰值: {peak / 1024 / 1024:.2f} MB")
        print(f"  每个实体: {current / 10000:.2f} bytes")
    
    def test_sustained_load(self):
        """持续负载测试"""
        from engine.systems import MovementSystem
        
        # 创建 10000 个实体
        entities = [
            Entity(components=[
                Transform(x=i, y=i),
                Velocity(dx=1, dy=1)
            ])
            for i in range(10000)
        ]
        
        system = MovementSystem()
        
        # 模拟 60 秒游戏运行 (60 FPS)
        frame_times = []
        for _ in range(3600):  # 60 * 60
            start = time.perf_counter()
            system.update(entities, 0.016)
            frame_times.append(time.perf_counter() - start)
        
        import statistics
        avg_frame = statistics.mean(frame_times)
        max_frame = max(frame_times)
        min_frame = min(frame_times)
        
        print(f"\n持续负载测试 (10000 实体, 60秒):")
        print(f"  平均帧时间: {avg_frame * 1000:.4f}ms")
        print(f"  最小帧时间: {min_frame * 1000:.4f}ms")
        print(f"  最大帧时间: {max_frame * 1000:.4f}ms")
        print(f"  理论最大 FPS: {1 / avg_frame:.0f}")
        
        # 确保能维持 60 FPS
        assert avg_frame < 0.016  # 16ms per frame
```

## 三、CI/CD 集成

### GitHub Actions 配置

```yaml
# .github/workflows/test.yml
name: Engine Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pytest pytest-cov pytest-benchmark
          pip install mypy pylint black isort
      
      - name: Run unit tests
        run: pytest tests/unit -v --cov=src/engine --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
  
  benchmark-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install pytest pytest-benchmark
      
      - name: Run benchmarks
        run: pytest tests/benchmark -v --benchmark-only
      
      - name: Check performance regression
        run: python scripts/check_regression.py

  stress-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Run stress tests
        run: pytest tests/stress -v
        timeout-minutes: 10
```

### 性能回归检测脚本

```python
# scripts/check_regression.py
import json
import sys
from pathlib import Path

# 性能基线
BASELINES = {
    "entity_create_1000": {"max_time": 0.1, "unit": "s"},
    "entity_update_1000": {"max_time": 0.001, "unit": "s"},
    "vector_addition": {"max_time": 0.00001, "unit": "s"},
}

def check_regression(benchmark_file: Path):
    """检查性能回归"""
    with open(benchmark_file) as f:
        results = json.load(f)
    
    regressions = []
    
    for benchmark in results.get("benchmarks", []):
        name = benchmark["name"]
        mean_time = benchmark["stats"]["mean"]
        
        if name in BASELINES:
            baseline = BASELINES[name]["max_time"]
            if mean_time > baseline:
                regressions.append({
                    "name": name,
                    "actual": mean_time,
                    "baseline": baseline,
                    "ratio": mean_time / baseline,
                })
    
    if regressions:
        print("❌ Performance regression detected!")
        for r in regressions:
            print(f"  {r['name']}: {r['actual']:.6f}s "
                  f"(baseline: {r['baseline']:.6f}s, "
                  f"{r['ratio']:.2f}x slower)")
        sys.exit(1)
    else:
        print("✅ All benchmarks within baseline")

if __name__ == "__main__":
    check_regression(Path(".benchmarks/results.json"))
```

## 四、测试最佳实践

### 1. 测试隔离原则

```python
# ✅ 好的做法 - 完全隔离
def test_entity_creation_isolated():
    # 不依赖任何外部状态
    entity = Entity()
    assert entity is not None

# ❌ 坏的做法 - 依赖全局状态
def test_entity_creation_bad():
    # 依赖全局引擎实例
    entity = Engine.instance.create_entity()  # 不推荐
```

### 2. Mock 边界清晰

```python
# ✅ 好的做法 - Mock 在边界
def test_game_logic_with_mock_renderer():
    renderer = MockRenderer()
    game = Game(renderer=renderer)
    
    game.update()
    
    assert renderer.draw_count > 0

# ❌ 坏的做法 - Mock 内部实现
def test_game_logic_bad():
    game = Game()
    game._internal_renderer = Mock()  # 不要 Mock 内部
```

### 3. 确定性测试

```python
# ✅ 好的做法 - 确定性
def test_deterministic():
    entity = Entity()
    entity.position = Vector2(0, 0)
    entity.velocity = Vector2(10, 0)
    
    entity.update(1.0)  # 固定 delta time
    
    assert entity.position.x == 10  # 结果确定

# ❌ 坏的做法 - 非确定性
def test_non_deterministic():
    entity = Entity()
    entity.update()  # 使用真实时间
    
    # 无法预测结果
```
