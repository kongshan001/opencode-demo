---
name: performance-opt
description: 游戏性能优化技巧和策略
license: MIT
metadata:
  category: optimization
---

## 性能优化技能

当需要优化游戏性能时使用此技能。

## 性能分析工具

### cProfile

```python
import cProfile
import pstats

# 分析代码
profiler = cProfile.Profile()
profiler.enable()

# 运行游戏代码
game.run()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # 显示前20个耗时函数
```

### timeit

```python
import timeit

# 测量函数执行时间
timeit.timeit('function()', setup='from __main__ import function', number=1000)
```

### 内存分析

```python
import tracemalloc

tracemalloc.start()

# 运行代码
game.run()

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

for stat in top_stats[:10]:
    print(stat)
```

## 优化策略

### 1. 减少函数调用

```python
# 慢
for entity in entities:
    entity.get_position().x += entity.get_velocity().dx * dt

# 快 - 缓存引用
for entity in entities:
            pos.x += vel.dx * dt
```

### 2. 使用 __slots__

```python
# 优化前
class Entity:
    def __init__(self):
        self.x = 0
        self.y = 0
        # 每个实例有 __dict__，占用大量内存

# 优化后
class Entity:
    __slots__ = ['x', 'y', 'active']
    
    def __init__(self):
        self.x = 0
        self.y = 0
        self.active = True
```

### 3. 避免频繁创建对象

```python
# 慢 - 每帧创建新列表
def update(entities):
    active = [e for e in entities if e.active]  # 每帧创建
    for entity in active:
        entity.update()

# 快 - 预分配列表
class Game:
    def __init__(self):
        self._temp_list = [None] * 1000  # 预分配
    
    def update(self, entities):
        count = 0
        for entity in entities:
            if entity.active:
                self._temp_list[count] = entity
                count += 1
        for i in range(count):
            self._temp_list[i].update()
```

### 4. 使用生成器

```python
# 占用大量内存
def get_all_positions(entities):
    return [e.position for e in entities]

# 内存友好
def get_all_positions(entities):
    for e in entities:
        yield e.position
```

### 5. 批量操作

```python
# 慢 - 多次调用
for sprite in sprites:
    renderer.draw(sprite)

# 快 - 批量渲染
renderer.draw_batch(sprites)
```

## 空间分区

### 网格分区

```python
class SpatialGrid:
    def __init__(self, cell_size: int):
        self.cell_size = cell_size
        self.grid: Dict[Tuple[int, int], List[Entity]] = {}
    
    def add(self, entity: Entity):
        cell = self._get_cell(entity.x, entity.y)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(entity)
    
    def _get_cell(self, x: float, y: float) -> Tuple[int, int]:
        return (int(x // self.cell_size), int(y // self.cell_size))
    
    def get_nearby(self, x: float, y: float, radius: float) -> List[Entity]:
        """获取附近实体"""
        result = []
        cell_radius = int(radius // self.cell_size) + 1
        cx, cy = self._get_cell(x, y)
        
        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                cell = (cx + dx, cy + dy)
                result.extend(self.grid.get(cell, []))
        
        return result
```

## 性能指标

### 帧率监控

```python
import time
from collections import deque

class FPSCounter:
    def __init__(self, sample_size: int = 60):
        self.samples = deque(maxlen=sample_size)
        self._last_time = time.perf_counter()
    
    def tick(self):
        current = time.perf_counter()
        dt = current - self._last_time
        self._last_time = current
        self.samples.append(dt)
    
    @property
    def fps(self) -> float:
        if not self.samples:
            return 0.0
        avg_dt = sum(self.samples) / len(self.samples)
        return 1.0 / avg_dt if avg_dt > 0 else 0.0
```

## 优化检查清单

- [ ] 使用 `__slots__` 减少内存
- [ ] 缓存频繁访问的属性
- [ ] 使用对象池复用对象
- [ ] 避免在循环中创建对象
- [ ] 使用空间分区优化碰撞检测
- [ ] 批量渲染减少 draw call
- [ ] 异步加载资源
- [ ] LOD (Level of Detail) 系统
