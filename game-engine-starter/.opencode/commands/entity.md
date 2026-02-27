---
description: 创建新实体类 $ARGUMENTS
---

创建一个名为 $ARGUMENTS 的游戏实体类。

## 创建步骤

1. 分析现有实体类的结构
2. 确定实体需要的组件
3. 创建实体类文件
4. 添加必要的类型注解

## 模板

```python
from dataclasses import dataclass
from typing import Optional
from engine.entity import Entity
from engine.components import Transform, Velocity

class $ARGUMENTS(Entity):
    \"\"\"$ARGUMENTS 实体类
    
    TODO: 添加类描述
    \"\"\"
    
    __slots__ = ['_specific_field']  # 添加特定字段
    
    def __init__(self, x: float = 0.0, y: float = 0.0):
        super().__init__()
        
        # 添加基础组件
        self.add_component(Transform(x=x, y=y))
        
        # TODO: 添加特定组件
    
    def update(self, dt: float) -> None:
        \"\"\"更新实体状态
        
        Args:
            dt: 增量时间（秒）
        \"\"\"
        # TODO: 实现更新逻辑
        pass
```

请根据项目现有的实体类结构进行适当调整。
