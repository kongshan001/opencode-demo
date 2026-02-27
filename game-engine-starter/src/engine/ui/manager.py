"""
UI 管理器 - 管理所有 UI 元素，支持测试交互
"""

from typing import Dict, List, Optional
from .element import UIElement


class UIManager:
    """UI 管理器"""
    
    def __init__(self):
        self._elements: Dict[str, UIElement] = {}
        self._root_elements: List[UIElement] = []
        self._focused_element: Optional[UIElement] = None
    
    def register(self, element: UIElement):
        """注册 UI 元素"""
        self._elements[element.element_id] = element
        if element.parent is None:
            self._root_elements.append(element)
    
    def unregister(self, element: UIElement):
        """注销 UI 元素"""
        if element.element_id in self._elements:
            del self._elements[element.element_id]
        if element in self._root_elements:
            self._root_elements.remove(element)
    
    def get_element(self, element_id: str) -> Optional[UIElement]:
        """通过 ID 获取元素"""
        return self._elements.get(element_id)
    
    def find_element_by_name(self, name: str) -> Optional[UIElement]:
        """通过名称查找元素"""
        for element in self._elements.values():
            if element.name == name:
                return element
        return None
    
    def find_element_by_path(self, path: str) -> Optional[UIElement]:
        """通过路径查找元素
        
        例如: "inventory_panel/item_slot_1"
        """
        parts = path.split("/")
        current = None
        
        for part in parts:
            if current is None:
                # 查找根元素
                for elem in self._root_elements:
                    if elem.element_id == part or elem.name == part:
                        current = elem
                        break
            else:
                # 查找子元素
                for child in current.children:
                    if child.element_id == part or child.name == part:
                        current = child
                        break
        
        return current
    
    def get_element_at(self, x: int, y: int) -> Optional[UIElement]:
        """获取指定坐标的最上层元素"""
        # 从后往前遍历（后添加的在上面）
        for element in reversed(list(self._elements.values())):
            if element.visible and element.contains_point(x, y):
                return element
        return None
    
    def click_at(self, x: int, y: int) -> bool:
        """点击指定坐标
        
        Returns:
            是否点击成功
        """
        element = self.get_element_at(x, y)
        if element and element.enabled:
            element.click()
            return True
        return False
    
    def click_element(
        self,
        element_id: str = None,
        name: str = None,
        path: str = None
    ) -> bool:
        """点击指定元素
        
        Args:
            element_id: 元素 ID
            name: 元素名称
            path: 元素路径
        
        Returns:
            是否点击成功
        """
        element = None
        
        if element_id:
            element = self.get_element(element_id)
        elif name:
            element = self.find_element_by_name(name)
        elif path:
            element = self.find_element_by_path(path)
        
        if element and element.visible and element.enabled:
            element.click()
            return True
        
        return False
    
    def list_elements(self, visible_only: bool = True) -> List[dict]:
        """列出所有元素"""
        elements = []
        for element in self._elements.values():
            if not visible_only or element.visible:
                elements.append(element.to_dict())
        return elements
    
    def get_hierarchy(self) -> dict:
        """获取 UI 层级结构"""
        def build_tree(element: UIElement) -> dict:
            return {
                **element.to_dict(),
                "children": [build_tree(child) for child in element.children]
            }
        
        return {
            "root_elements": [build_tree(e) for e in self._root_elements]
        }
    
    def clear(self):
        """清空所有元素"""
        self._elements.clear()
        self._root_elements.clear()
        self._focused_element = None
