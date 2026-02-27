"""
UI 元素基类
"""

from typing import List, Optional


class UIElement:
    """UI 元素基类"""
    
    def __init__(self, element_id: str, name: str = ""):
        self.element_id = element_id  # 唯一 ID
        self.name = name              # 可读名称
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.visible = True
        self.enabled = True
        self.parent: Optional['UIElement'] = None
        self.children: List['UIElement'] = []
    
    def get_bounds(self):
        """获取边界 (left, top, right, bottom)"""
        return (self.x, self.y, self.x + self.width, self.y + self.height)
    
    def contains_point(self, x: int, y: int) -> bool:
        """检查点是否在元素内"""
        return (self.x <= x < self.x + self.width and
                self.y <= y < self.y + self.height)
    
    def click(self):
        """点击事件 - 子类重写"""
        pass
    
    def add_child(self, child: 'UIElement'):
        """添加子元素"""
        child.parent = self
        self.children.append(child)
    
    def to_dict(self):
        """序列化为字典"""
        return {
            "id": self.element_id,
            "name": self.name,
            "type": self.__class__.__name__,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "visible": self.visible,
            "enabled": self.enabled,
        }
