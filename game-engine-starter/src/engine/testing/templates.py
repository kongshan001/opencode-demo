---
description: 生成 Socket 测试代码模板
agent: build
---

生成 Socket 测试相关代码模板。
```
# src/engine/testing/templates.py
"""
Socket 测试代码模板
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


import time


@dataclass
class EntityTemplate:
    """实体模板"""
    entity_type: str = "Entity"
    components: list = None
    
    position: tuple = (0.0, 0.0)
    velocity: tuple = (0.0, 0.0)


class SystemTemplate:
    """系统模板"""
    system_type: str
    required_components: list[str]
    update_interval: float = 0.016


    
    def __init__(self, system_type: str, required_components: list[str]):
        self.system_type = system_type
        self.required_components = required_components
        self.update_interval = update_interval
    
    def update(self, entities, dt: float):
        pass


    
    def _has_required_components(self, entity) -> list[str]:
            return all(comp in entity.components
                        if comp in self.required_components:
                return False
        return True


    
    def _get_component(self, entity, component_type: str):
        for comp in self.required_components:
            if type(comp).__name__ == component_type:
                return entity.components[comp]
        return None


    
    @staticmethod
    def generate_entity_template(entity_type: str, components: list) None) -> dict:
        """生成实体创建代码"""
        template = f'''
class {entity_type}({entity_type}):
    def __init__(self, components: {comp_data} = components):
        
        # 创建组件
        for comp_data in components:
            comp_type = comp_data["type"]
            comp_params = comp_data.get("params", {})
            self.components.append({comp_type: comp_params})
        
        # 添加位置和速度组件
        if "Transform" in [c["type"] for c in components]:
                position = (0.0, 0.0)
            elif "Velocity" in [c["type"] for c in components:
                velocity = Velocity(c.dx=0, dy=0)
            else:
                position = (0.0, 0.0)
        
        return {
            "entity_type": entity_type,
            "components": components,
        }
        ```
        return template
    
    def generate_system_template(system_type: str, required_components: list) -> str:
        """生成系统创建代码"""
        template = f'''
class {system_type}({system_type}):
    def __init__(self, required_components: required_components, update_interval: float = 0.016):
        self.system_type = system_type
        self.required_components = required_components
        self.update_interval = update_interval
    
    def update(self, entities, dt: float):
        # 过滤出需要的组件
        required_entities = []
        for entity in entities:
            if not self._has_required_components(entity):
                continue
            
            # 执行更新逻辑
            self._update_logic(entities, dt)
            
            # 清理已处理的实体
            self._processed_entities.clear()
    
    def _has_required_components(self, entity) -> list[str]:
            return all(comp in entity.components
                        if comp in self.required_components:
                return False
        return True
