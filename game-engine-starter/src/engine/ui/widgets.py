"""
UI 组件示例
"""

from .element import UIElement
from typing import Callable, Optional, Any


class Button(UIElement):
    """按钮组件"""
    
    def __init__(
        self,
        element_id: str,
        name: str = "",
        on_click: Callable[[], None] = None
    ):
        super().__init__(element_id, name)
        self.on_click = on_click
        self.text = ""
    
    def click(self):
        """点击按钮"""
        if self.enabled and self.on_click:
            self.on_click()
    
    def to_dict(self):
        return {
            **super().to_dict(),
            "text": self.text,
        }


class ItemSlot(UIElement):
    """道具槽组件"""
    
    def __init__(self, element_id: str, slot_index: int = 0):
        super().__init__(element_id, f"道具槽_{slot_index}")
        self.slot_index = slot_index
        self.item: Optional[dict] = None
        self.on_click: Optional[Callable[[dict], None]] = None
    
    def click(self):
        """点击道具槽"""
        if self.enabled:
            if self.on_click and self.item:
                self.on_click(self.item)
    
    def set_item(self, item: dict):
        """设置道具"""
        self.item = item
    
    def clear_item(self):
        """清空道具"""
        self.item = None
    
    def to_dict(self):
        return {
            **super().to_dict(),
            "slot_index": self.slot_index,
            "item": self.item,
        }


class InventoryPanel(UIElement):
    """背包面板"""
    
    def __init__(
        self,
        element_id: str = "inventory_panel",
        slot_count: int = 20,
        cols: int = 5
    ):
        super().__init__(element_id, "背包")
        self.x = 100
        self.y = 100
        self.width = 400
        self.height = 300
        self.slot_count = slot_count
        self.cols = cols
        
        # 创建道具槽
        self.slots: list[ItemSlot] = []
        self._create_slots()
    
    def _create_slots(self):
        """创建道具槽"""
        slot_size = 70
        padding = 6
        
        for i in range(self.slot_count):
            slot = ItemSlot(f"item_slot_{i}", i)
            col = i % self.cols
            row = i // self.cols
            slot.x = 10 + col * (slot_size + padding)
            slot.y = 40 + row * (slot_size + padding)
            slot.width = slot_size
            slot.height = slot_size
            slot.parent = self
            self.children.append(slot)
            self.slots.append(slot)
    
    def get_slot(self, index: int) -> Optional[ItemSlot]:
        """获取指定索引的道具槽"""
        if 0 <= index < len(self.slots):
            return self.slots[index]
        return None
    
    def find_slot_by_item_id(self, item_id: str) -> Optional[ItemSlot]:
        """通过道具 ID 查找槽位"""
        for slot in self.slots:
            if slot.item and slot.item.get("id") == item_id:
                return slot
        return None
    
    def add_item(self, item: dict) -> bool:
        """添加道具到第一个空槽"""
        for slot in self.slots:
            if slot.item is None:
                slot.set_item(item)
                return True
        return False
    
    def remove_item(self, item_id: str) -> bool:
        """移除道具"""
        slot = self.find_slot_by_item_id(item_id)
        if slot:
            slot.clear_item()
            return True
        return False
    
    def to_dict(self):
        return {
            **super().to_dict(),
            "slot_count": self.slot_count,
            "used_slots": sum(1 for s in self.slots if s.item),
        }


class Panel(UIElement):
    """通用面板"""
    
    def __init__(self, element_id: str, name: str = ""):
        super().__init__(element_id, name)
        self.title = ""
        self.draggable = False
        self.modal = False
    
    def to_dict(self):
        return {
            **super().to_dict(),
            "title": self.title,
            "draggable": self.draggable,
            "modal": self.modal,
        }


class Label(UIElement):
    """文本标签"""
    
    def __init__(self, element_id: str, text: str = ""):
        super().__init__(element_id, text)
        self.text = text
    
    def to_dict(self):
        return {
            **super().to_dict(),
            "text": self.text,
        }


class CheckBox(UIElement):
    """复选框"""
    
    def __init__(self, element_id: str, name: str = "", checked: bool = False):
        super().__init__(element_id, name)
        self.checked = checked
        self.on_change: Optional[Callable[[bool], None]] = None
    
    def click(self):
        """点击切换状态"""
        if self.enabled:
            self.checked = not self.checked
            if self.on_change:
                self.on_change(self.checked)
    
    def to_dict(self):
        return {
            **super().to_dict(),
            "checked": self.checked,
        }


class Slider(UIElement):
    """滑块"""
    
    def __init__(
        self,
        element_id: str,
        name: str = "",
        min_value: float = 0,
        max_value: float = 100,
        value: float = 50
    ):
        super().__init__(element_id, name)
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.on_change: Optional[Callable[[float], None]] = None
    
    def set_value(self, value: float):
        """设置值"""
        self.value = max(self.min_value, min(self.max_value, value))
        if self.on_change:
            self.on_change(self.value)
    
    def click(self):
        """点击（测试用）"""
        pass
    
    def to_dict(self):
        return {
            **super().to_dict(),
            "min_value": self.min_value,
            "max_value": self.max_value,
            "value": self.value,
        }
