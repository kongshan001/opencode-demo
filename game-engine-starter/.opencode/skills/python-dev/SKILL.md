---
name: python-dev
description: Python 开发最佳实践和代码规范
license: MIT
metadata:
  category: development
  language: python
---

## Python 开发技能

当你需要进行 Python 开发时使用此技能。

## 代码规范

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
DEFAULT_FPS = 60

# 私有成员: _leading_underscore
class Entity:
    def __init__(self):
        self._internal_state = None
```

### 类型注解

```python
from typing import List, Optional, Dict, Tuple

def spawn_entity(
    position: Tuple[float, float],
    velocity: Optional[Tuple[float, float]] = None
) -> Entity:
    """生成新实体
    
    Args:
        position: 实体位置 (x, y)
        velocity: 可选的初始速度
    
    Returns:
        新创建的实体
    """
    pass
```

### 文档字符串

```python
def update(delta_time: float) -> None:
    """更新游戏状态
    
    Args:
        delta_time: 距离上一帧的时间（秒）
    
    Raises:
        ValueError: 如果 delta_time 为负数
    
    Note:
        此方法每帧调用一次
    """
    pass
```

## 项目结构

```
game_project/
├── src/
│   ├── engine/           # 引擎核心
│   │   ├── __init__.py
│   │   ├── core.py
│   │   ├── renderer.py
│   │   └── physics.py
│   ├── game/             # 游戏逻辑
│   │   ├── __init__.py
│   │   ├── entities.py
│   │   └── scenes.py
│   └── utils/            # 工具函数
├── tests/                # 测试
├── assets/               # 资源文件
├── main.py               # 入口
└── pyproject.toml        # 项目配置
```

## 常用工具

- **代码格式化**: `black .`
- **导入排序**: `isort .`
- **类型检查**: `mypy src/`
- **代码检查**: `pylint src/`
- **测试**: `pytest tests/`

## 注意事项

- 避免在游戏循环中使用 `.` 操作符查找属性（缓存引用）
- 使用 `__slots__` 减少内存占用
- 避免频繁创建/销毁对象（使用对象池）
- 使用生成器减少内存使用
