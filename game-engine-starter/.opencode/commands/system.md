---
description: 创建新系统类 $ARGUMENTS
---

创建一个名为 $ARGUMENTS 的游戏系统类。

## 创建步骤

1. 分析现有系统类的结构
2. 确定系统处理的组件类型
3. 创建系统类文件

## 模板

```python
from typing import List, Type
from engine.system import System
from engine.entity import Entity
from engine.components import Component

class $ARGUMENTS(System):
    \"\"\"$ARGUMENTS 系统类
    
    处理 [组件类型] 组件
    \"\"\"
    
    @property
    def required_components(self) -> List[Type[Component]]:
        \"\"\"返回此系统需要的组件类型\"\"\"
        return [
            # TODO: 添加需要的组件类型
        ]
    
    def update(self, entities: List[Entity], dt: float) -> None:
        \"\"\"更新所有符合条件的实体
        
        Args:
            entities: 所有实体列表
            dt: 增量时间（秒）
        \"\"\"
        for entity in entities:
            if self._has_required_components(entity):
                self._process_entity(entity, dt)
    
    def _has_required_components(self, entity: Entity) -> bool:
        \"\"\"检查实体是否有所有需要的组件\"\"\"
        return all(
            entity.get_component(comp) is not None
            for comp in self.required_components
        )
    
    def _process_entity(self, entity: Entity, dt: float) -> None:
        \"\"\"处理单个实体
        
        Args:
            entity: 要处理的实体
            dt: 增量时间（秒）
        \"\"\"
        # TODO: 实现处理逻辑
        pass
```

请根据项目现有的系统类结构进行适当调整。
