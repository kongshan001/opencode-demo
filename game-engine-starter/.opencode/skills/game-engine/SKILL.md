---
name: game-engine
description: 游戏引擎开发模式和最佳实践
license: MIT
metadata:
  category: game-development
---

## 游戏引擎技能

当开发游戏引擎相关功能时使用此技能。

## 核心架构

### 游戏循环

```python
import time

class Game:
    def __init__(self):
        self.is_running = False
        self.target_fps = 60
        self._last_time = 0
    
    def run(self):
        """主游戏循环"""
        self.is_running = True
        self._last_time = time.perf_counter()
        
        while self.is_running:
            # 计算增量时间
            current_time = time.perf_counter()
            delta_time = current_time - self._last_time
            self._last_time = current_time
            
            # 固定时间步长更新
            self._update(delta_time)
            
            # 渲染
            self._render()
            
            # 帧率控制
            self._limit_fps()
    
    def _update(self, dt: float):
        """更新游戏逻辑"""
        pass
    
    def _render(self):
        """渲染画面"""
        pass
    
    def _limit_fps(self):
        """限制帧率"""
        frame_time = 1.0 / self.target_fps
        elapsed = time.perf_counter() - self._last_time
        if elapsed < frame_time:
            time.sleep(frame_time - elapsed)
```

### 实体组件系统 (ECS)

```python
from dataclasses import dataclass
from typing import Dict, Type, Any

@dataclass
class Component:
    """组件基类"""
    pass

@dataclass
class Transform(Component):
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0

@dataclass
class Velocity(Component):
    dx: float = 0.0
    dy: float = 0.0

class Entity:
    """实体 - 组件容器"""
    __slots__ = ['id', 'components', 'is_active']
    
    def __init__(self, entity_id: int):
        self.id = entity_id
        self.components: Dict[Type[Component], Component] = {}
        self.is_active = True
    
    def add_component(self, component: Component):
        self.components[type(component)] = component
    
    def get_component(self, component_type: Type[T]) -> Optional[T]:
        return self.components.get(component_type)

class System:
    """系统 - 处理特定组件"""
    def update(self, entities: List[Entity], dt: float):
        pass

class MovementSystem(System):
    def update(self, entities: List[Entity], dt: float):
        for entity in entities:
            transform = entity.get_component(Transform)
            velocity = entity.get_component(Velocity)
            
            if transform and velocity:
                transform.x += velocity.dx * dt
                transform.y += velocity.dy * dt
```

### 对象池

```python
from typing import Generic, TypeVar, List

T = TypeVar('T')

class ObjectPool(Generic[T]):
    """通用对象池"""
    
    def __init__(self, factory: callable, initial_size: int = 10):
        self.factory = factory
        self.pool: List[T] = []
        self._expand(initial_size)
    
    def _expand(self, count: int):
        for _ in range(count):
            self.pool.append(self.factory())
    
    def acquire(self) -> T:
        if not self.pool:
            self._expand(5)
        return self.pool.pop()
    
    def release(self, obj: T):
        self.pool.append(obj)
```

### 事件系统

```python
from typing import Callable, Dict, List
from dataclasses import dataclass

@dataclass
class Event:
    """事件基类"""
    pass

EventHandler = Callable[[Event], None]

class EventBus:
    """事件总线"""
    
    def __init__(self):
        self._handlers: Dict[type, List[EventHandler]] = {}
    
    def subscribe(self, event_type: type, handler: EventHandler):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: type, handler: EventHandler):
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)
    
    def emit(self, event: Event):
        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            handler(event)
```

## 设计模式

### 单例模式（用于管理器）

```python
class GameManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 状态模式（用于游戏状态）

```python
class GameState(ABC):
    @abstractmethod
    def enter(self): pass
    
    @abstractmethod
    def update(self, dt: float): pass
    
    @abstractmethod
    def exit(self): pass

class PlayingState(GameState):
    def enter(self):
        print("进入游戏")
    
    def update(self, dt: float):
        # 游戏逻辑
        pass
```

## 性能优化

1. **缓存引用**: 避免重复属性查找
2. **使用 `__slots__`**: 减少内存占用
3. **对象池**: 复用对象减少 GC
4. **空间分区**: 加速碰撞检测
5. **批量渲染**: 减少 draw call
