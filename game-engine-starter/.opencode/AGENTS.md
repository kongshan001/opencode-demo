# Python 游戏引擎项目

这是一个基于 Python 和自研游戏引擎的游戏开发项目。

## 技术栈

- **语言**: Python 3.10+
- **引擎**: 自研游戏引擎
- **测试**: pytest
- **类型检查**: mypy
- **代码格式**: black, isort

## 项目结构

```
game_project/
├── src/
│   ├── engine/           # 引擎核心
│   │   ├── __init__.py
│   │   ├── core.py       # 核心类
│   │   ├── entity.py     # 实体类
│   │   ├── component.py  # 组件类
│   │   ├── system.py     # 系统类
│   │   ├── renderer.py   # 渲染器
│   │   └── physics.py    # 物理系统
│   ├── game/             # 游戏逻辑
│   │   ├── __init__.py
│   │   ├── entities/     # 游戏实体
│   │   ├── systems/      # 游戏系统
│   │   └── scenes/       # 游戏场景
│   └── utils/            # 工具函数
├── tests/                # 测试文件
├── assets/               # 游戏资源
│   ├── sprites/
│   ├── sounds/
│   └── fonts/
├── main.py               # 游戏入口
└── pyproject.toml        # 项目配置
```

## 代码规范

### Python 规范

- 遵循 PEP 8
- 使用类型注解
- 编写文档字符串
- 最大行长度: 88 (black 默认)

### 命名约定

```python
# 类名: PascalCase
class GameEngine:
    pass

# 函数/变量: snake_case
def calculate_fps():
    frame_count = 0

# 常量: UPPER_SNAKE_CASE
MAX_ENTITIES = 1000
TARGET_FPS = 60

# 私有成员: _leading_underscore
class Entity:
    def __init__(self):
        self._internal_state = None

# 保护成员: __double_underscore (名称修饰)
class Singleton:
    __instance = None
```

### 类型注解

```python
from typing import List, Optional, Dict, Tuple, TypeVar, Generic

T = TypeVar('T')

def spawn_entity(
    position: Tuple[float, float],
    velocity: Optional[Tuple[float, float]] = None
) -> Entity:
    """生成新实体"""
    pass

class Pool(Generic[T]):
    def acquire(self) -> T:
        pass
```

## 游戏开发规范

### 实体组件系统 (ECS)

```python
# 实体: 只包含数据和组件引用
class Entity:
    __slots__ = ['id', 'components', 'active']
    
    def __init__(self, entity_id: int):
        self.id = entity_id
        self.components: Dict[Type[Component], Component] = {}
        self.active = True

# 组件: 纯数据容器
@dataclass
class Transform(Component):
    x: float = 0.0
    y: float = 0.0

# 系统: 处理逻辑
class MovementSystem(System):
    def update(self, entities: List[Entity], dt: float):
        for entity in entities:
            # 处理逻辑
            pass
```

### 游戏循环

```python
class Game:
    def run(self):
        while self.is_running:
            dt = self._calculate_delta_time()
            
            self._handle_events()
            self._update(dt)
            self._render()
            
            self._limit_fps()
```

### 性能优化

1. **使用 `__slots__`** - 减少内存占用
2. **缓存引用** - 避免重复属性查找
3. **对象池** - 复用对象减少 GC
4. **批量操作** - 减少 API 调用次数

## 开发工作流

### 1. 创建新实体

```bash
/entity Player
```

### 2. 创建新系统

```bash
/system Movement
```

### 3. 运行游戏

```bash
/run
```

### 4. 运行测试

```bash
/test
```

### 5. 代码检查

```bash
/lint
```

### 6. 性能分析

```bash
/profile
```

## 禁止操作

- 不要直接修改引擎核心代码（除非必要）
- 不要在游戏循环中创建对象（使用对象池）
- 不要跳过类型检查警告
- 不要提交未格式化的代码
- 不要硬编码资源路径

## 资源管理

### 加载资源

```python
from engine.resources import ResourceLoader

# 同步加载
sprite = ResourceLoader.load_sprite("player.png")

# 异步加载
await ResourceLoader.load_sprite_async("background.png")
```

### 资源缓存

所有资源自动缓存，重复加载不会重新读取文件。

## 调试技巧

### 启用调试模式

```python
# main.py
import os
os.environ["GAME_DEBUG"] = "1"
```

### 日志记录

```python
from engine.logger import get_logger

logger = get_logger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
```

## 可用代理

- `@python-reviewer` - Python 代码审查
- `@performance-analyst` - 性能分析
- `@game-tester` - 测试编写

## 可用技能

- `python-dev` - Python 开发最佳实践
- `game-engine` - 游戏引擎模式
- `performance-opt` - 性能优化技巧
