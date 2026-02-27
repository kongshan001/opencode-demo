"""
游戏端 Socket 服务器 - 用于接收测试指令

使用方法:
1. 在游戏入口导入此模块
2. 检查测试模式配置
3. 创建 GameTestServer 并启动
4. 实现必要的指令处理器
"""

import socket
import json
import threading
import traceback
import time
from typing import Callable, Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class CommandType(Enum):
    """标准指令类型"""
    # 实体操作
    ENTITY_CREATE = "entity.create"
    ENTITY_GET = "entity.get"
    ENTITY_DELETE = "entity.delete"
    ENTITY_LIST = "entity.list"
    
    # 组件操作
    COMPONENT_GET = "component.get"
    COMPONENT_SET = "component.set"
    
    # 游戏控制
    GAME_PAUSE = "game.pause"
    GAME_RESUME = "game.resume"
    GAME_STEP = "game.step"
    GAME_RESET = "game.reset"
    
    # 状态
    STATE_GET = "state.get"
    STATE_SET = "state.set"
    
    # 输入
    INPUT_KEY = "input.key"
    INPUT_MOUSE = "input.mouse"
    
    # 性能
    PERF_FPS = "perf.fps"
    PERF_MEMORY = "perf.memory"
    
    # 渲染
    RENDER_COUNT = "render.count"
    
    # UI 操作
    UI_CLICK = "ui.click"
    UI_CLICK_AT = "ui.click_at"
    UI_GET_ELEMENT = "ui.get_element"
    UI_LIST_ELEMENTS = "ui.list_elements"
    UI_GET_HIERARCHY = "ui.get_hierarchy"
    UI_WAIT_FOR_ELEMENT = "ui.wait_for_element"
    
    # 道具操作
    ITEM_USE = "item.use"
    ITEM_EQUIP = "item.equip"
    ITEM_DROP = "item.drop"
    ITEM_GET_INFO = "item.get_info"


@dataclass
class TestCommand:
    """测试指令"""
    id: str
    type: str
    params: Dict[str, Any]
    timeout: float = 5.0


class GameTestServer:
    """
    游戏内嵌测试服务器
    
    在游戏中启动，监听测试指令并执行
    """
    
    def __init__(self, game, host: str = "localhost", port: int = 9876):
        """
        Args:
            game: 游戏实例（需要有 create_entity, get_entity 等方法）
            host: 监听地址
            port: 监听端口
        """
        self.game = game
        self.host = host
        self.port = port
        
        self._socket: Optional[socket.socket] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        # 注册标准处理器
        self._handlers: Dict[str, Callable] = {
            CommandType.ENTITY_CREATE.value: self._handle_entity_create,
            CommandType.ENTITY_GET.value: self._handle_entity_get,
            CommandType.ENTITY_LIST.value: self._handle_entity_list,
            CommandType.COMPONENT_GET.value: self._handle_component_get,
            CommandType.COMPONENT_SET.value: self._handle_component_set,
            CommandType.GAME_PAUSE.value: self._handle_game_pause,
            CommandType.GAME_RESUME.value: self._handle_game_resume,
            CommandType.GAME_STEP.value: self._handle_game_step,
            CommandType.STATE_GET.value: self._handle_state_get,
            CommandType.STATE_SET.value: self._handle_state_set,
            CommandType.INPUT_KEY.value: self._handle_input_key,
            CommandType.PERF_FPS.value: self._handle_perf_fps,
            CommandType.RENDER_COUNT.value: self._handle_render_count,
            
            # UI 操作
            CommandType.UI_CLICK.value: self._handle_ui_click,
            CommandType.UI_CLICK_AT.value: self._handle_ui_click_at,
            CommandType.UI_GET_ELEMENT.value: self._handle_ui_get_element,
            CommandType.UI_LIST_ELEMENTS.value: self._handle_ui_list_elements,
            CommandType.UI_GET_HIERARCHY.value: self._handle_ui_get_hierarchy,
            CommandType.UI_WAIT_FOR_ELEMENT.value: self._handle_ui_wait_for_element,
            
            # 道具操作
            CommandType.ITEM_USE.value: self._handle_item_use,
            CommandType.ITEM_EQUIP.value: self._handle_item_equip,
            CommandType.ITEM_DROP.value: self._handle_item_drop,
            CommandType.ITEM_GET_INFO.value: self._handle_item_get_info,
        }
        
        # 自定义处理器
        self._custom_handlers: Dict[str, Callable] = {}
    
    def register_handler(self, command_type: str, handler: Callable):
        """注册自定义指令处理器
        
        Args:
            command_type: 指令类型，如 "custom.my_action"
            handler: 处理函数，接收 params dict，返回结果 dict
        """
        self._custom_handlers[command_type] = handler
    
    def start(self):
        """启动服务器"""
        if self._running:
            return
        
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.host, self.port))
        self._socket.listen(1)
        self._socket.settimeout(1.0)
        
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        
        print(f"[TestServer] Started on {self.host}:{self.port}")
    
    def stop(self):
        """停止服务器"""
        self._running = False
        if self._socket:
            self._socket.close()
        if self._thread:
            self._thread.join(timeout=2.0)
        print("[TestServer] Stopped")
    
    def _run(self):
        """服务器主循环"""
        while self._running:
            try:
                conn, addr = self._socket.accept()
                
                with conn:
                    while self._running:
                        data = self._recv_message(conn)
                        if not data:
                            break
                        
                        response = self._handle_message(data)
                        self._send_message(conn, response)
                        
            except socket.timeout:
                continue
            except Exception as e:
                if self._running:
                    print(f"[TestServer] Error: {e}")
    
    def _recv_message(self, conn) -> Optional[dict]:
        """接收消息（4字节长度前缀 + JSON）"""
        length_data = conn.recv(4)
        if not length_data:
            return None
        
        length = int.from_bytes(length_data, 'big')
        data = b''
        
        while len(data) < length:
            chunk = conn.recv(min(4096, length - len(data)))
            if not chunk:
                return None
            data += chunk
        
        return json.loads(data.decode('utf-8'))
    
    def _send_message(self, conn, message: dict):
        """发送消息（4字节长度前缀 + JSON）"""
        data = json.dumps(message).encode('utf-8')
        length = len(data).to_bytes(4, 'big')
        conn.sendall(length + data)
    
    def _handle_message(self, data: dict) -> dict:
        """处理消息"""
        start_time = time.perf_counter()
        
        try:
            command_type = data.get("type", "")
            params = data.get("params", {})
            
            # 查找处理器
            handler = self._handlers.get(command_type)
            if handler is None:
                handler = self._custom_handlers.get(command_type)
            
            if handler is None:
                raise ValueError(f"Unknown command: {command_type}")
            
            # 执行
            result = handler(params)
            duration = time.perf_counter() - start_time
            
            return {
                "id": data.get("id", ""),
                "success": True,
                "result": result,
                "error": None,
                "duration": duration,
            }
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            return {
                "id": data.get("id", ""),
                "success": False,
                "result": None,
                "error": f"{type(e).__name__}: {str(e)}",
                "duration": duration,
            }
    
    # ============================================================
    # 标准指令处理器 - 需要根据你的游戏实现修改
    # ============================================================
    
    def _handle_entity_create(self, params: dict) -> dict:
        """创建实体
        
        需要在你的游戏类中实现: game.create_entity(entity_type)
        """
        entity_type = params.get("type", "Entity")
        components = params.get("components", [])
        
        # TODO: 实现你的实体创建逻辑
        if hasattr(self.game, 'create_entity'):
            entity = self.game.create_entity(entity_type)
            
            # 添加组件
            for comp in components:
                if hasattr(entity, 'add_component'):
                    entity.add_component(comp.get("type"), **comp.get("params", {}))
            
            return {"entity_id": entity.id if hasattr(entity, 'id') else 0}
        else:
            raise NotImplementedError("game.create_entity() not implemented")
    
    def _handle_entity_get(self, params: dict) -> dict:
        """获取实体"""
        entity_id = params["entity_id"]
        
        if hasattr(self.game, 'get_entity'):
            entity = self.game.get_entity(entity_id)
            if entity is None:
                raise ValueError(f"Entity not found: {entity_id}")
            
            return {
                "id": entity_id,
                "active": getattr(entity, 'is_active', True),
            }
        else:
            raise NotImplementedError("game.get_entity() not implemented")
    
    def _handle_entity_list(self, params: dict) -> dict:
        """列出所有实体"""
        if hasattr(self.game, 'get_entities'):
            entities = self.game.get_entities()
            return {
                "count": len(entities),
                "entities": [{"id": getattr(e, 'id', i)} for i, e in enumerate(entities)]
            }
        else:
            return {"count": 0, "entities": []}
    
    def _handle_component_get(self, params: dict) -> dict:
        """获取组件"""
        entity_id = params["entity_id"]
        component_type = params["component_type"]
        
        if hasattr(self.game, 'get_entity'):
            entity = self.game.get_entity(entity_id)
            if entity and hasattr(entity, 'get_component'):
                comp = entity.get_component(component_type)
                if comp and hasattr(comp, 'to_dict'):
                    return comp.to_dict()
                elif comp:
                    return {"_type": component_type}
        
        raise ValueError(f"Component not found: {component_type}")
    
    def _handle_component_set(self, params: dict) -> dict:
        """设置组件属性"""
        entity_id = params["entity_id"]
        component_type = params["component_type"]
        properties = params["properties"]
        
        if hasattr(self.game, 'get_entity'):
            entity = self.game.get_entity(entity_id)
            if entity and hasattr(entity, 'get_component'):
                comp = entity.get_component(component_type)
                if comp:
                    for key, value in properties.items():
                        setattr(comp, key, value)
                    return {"success": True}
        
        raise ValueError(f"Failed to set component properties")
    
    def _handle_game_pause(self, params: dict) -> dict:
        """暂停游戏"""
        if hasattr(self.game, 'pause'):
            self.game.pause()
        elif hasattr(self.game, 'is_paused'):
            self.game.is_paused = True
        
        return {"paused": True}
    
    def _handle_game_resume(self, params: dict) -> dict:
        """恢复游戏"""
        if hasattr(self.game, 'resume'):
            self.game.resume()
        elif hasattr(self.game, 'is_paused'):
            self.game.is_paused = False
        
        return {"paused": False}
    
    def _handle_game_step(self, params: dict) -> dict:
        """单步执行"""
        dt = params.get("dt", 0.016)
        
        if hasattr(self.game, 'step'):
            self.game.step(dt)
        elif hasattr(self.game, 'update'):
            self.game.update(dt)
        
        return {"stepped": True, "dt": dt}
    
    def _handle_state_get(self, params: dict) -> dict:
        """获取游戏状态"""
        key = params.get("key")
        
        if key:
            value = getattr(self.game, key, None)
            return {"value": value}
        else:
            # 返回所有状态
            return {}
    
    def _handle_state_set(self, params: dict) -> dict:
        """设置游戏状态"""
        key = params["key"]
        value = params["value"]
        
        if hasattr(self.game, key):
            setattr(self.game, key, value)
            return {"success": True}
        else:
            raise ValueError(f"Unknown state: {key}")
    
    def _handle_input_key(self, params: dict) -> dict:
        """模拟按键"""
        key = params["key"]
        action = params.get("action", "tap")
        
        if hasattr(self.game, 'input'):
            if action == "press":
                self.game.input.key_press(key)
            elif action == "release":
                self.game.input.key_release(key)
            elif action == "tap":
                if hasattr(self.game.input, 'key_tap'):
                    self.game.input.key_tap(key)
                else:
                    self.game.input.key_press(key)
                    self.game.input.key_release(key)
        
        return {"success": True}
    
    def _handle_perf_fps(self, params: dict) -> dict:
        """获取 FPS"""
        fps = getattr(self.game, 'fps', 0)
        frame_time = getattr(self.game, 'frame_time', 0)
        
        return {"fps": fps, "frame_time": frame_time}
    
    def _handle_render_count(self, params: dict) -> dict:
        """获取渲染次数"""
        renderer = getattr(self.game, 'renderer', None)
        draw_count = getattr(renderer, 'draw_count', 0) if renderer else 0
        
        return {"draw_calls": draw_count}
    
    # ============================================================
    # UI 操作指令处理器
    # ============================================================
    
    def _handle_ui_click(self, params: dict) -> dict:
        """点击 UI 元素
        
        参数:
            - element_id: 元素 ID
            - name: 元素名称
            - path: 元素路径（如 "inventory_panel/item_slot_0"）
        """
        ui_manager = self._get_ui_manager()
        if not ui_manager:
            raise NotImplementedError("UI manager not available")
        
        element_id = params.get("element_id")
        name = params.get("name")
        path = params.get("path")
        
        success = ui_manager.click_element(
            element_id=element_id,
            name=name,
            path=path
        )
        
        return {
            "success": success,
            "element_id": element_id,
            "name": name,
            "path": path,
        }
    
    def _handle_ui_click_at(self, params: dict) -> dict:
        """点击指定坐标
        
        参数:
            - x: X 坐标
            - y: Y 坐标
        """
        ui_manager = self._get_ui_manager()
        if not ui_manager:
            raise NotImplementedError("UI manager not available")
        
        x = params["x"]
        y = params["y"]
        
        # 获取点击的元素
        element = ui_manager.get_element_at(x, y)
        element_info = element.to_dict() if element else None
        
        # 执行点击
        success = ui_manager.click_at(x, y)
        
        return {
            "success": success,
            "x": x,
            "y": y,
            "element": element_info,
        }
    
    def _handle_ui_get_element(self, params: dict) -> dict:
        """获取 UI 元素信息
        
        参数:
            - element_id: 元素 ID
            - name: 元素名称
            - path: 元素路径
        """
        ui_manager = self._get_ui_manager()
        if not ui_manager:
            raise NotImplementedError("UI manager not available")
        
        element_id = params.get("element_id")
        name = params.get("name")
        path = params.get("path")
        
        element = None
        if element_id:
            element = ui_manager.get_element(element_id)
        elif name:
            element = ui_manager.find_element_by_name(name)
        elif path:
            element = ui_manager.find_element_by_path(path)
        
        if element is None:
            raise ValueError("Element not found")
        
        return element.to_dict()
    
    def _handle_ui_list_elements(self, params: dict) -> dict:
        """列出所有 UI 元素"""
        ui_manager = self._get_ui_manager()
        if not ui_manager:
            raise NotImplementedError("UI manager not available")
        
        visible_only = params.get("visible_only", True)
        elements = ui_manager.list_elements(visible_only)
        
        return {
            "count": len(elements),
            "elements": elements,
        }
    
    def _handle_ui_get_hierarchy(self, params: dict) -> dict:
        """获取 UI 层级结构"""
        ui_manager = self._get_ui_manager()
        if not ui_manager:
            raise NotImplementedError("UI manager not available")
        
        return ui_manager.get_hierarchy()
    
    def _handle_ui_wait_for_element(self, params: dict) -> dict:
        """等待元素出现
        
        参数:
            - element_id: 元素 ID
            - name: 元素名称
            - timeout: 超时时间（秒）
        """
        ui_manager = self._get_ui_manager()
        if not ui_manager:
            raise NotImplementedError("UI manager not available")
        
        element_id = params.get("element_id")
        name = params.get("name")
        timeout = params.get("timeout", 5.0)
        
        start = time.perf_counter()
        
        while time.perf_counter() - start < timeout:
            element = None
            if element_id:
                element = ui_manager.get_element(element_id)
            elif name:
                element = ui_manager.find_element_by_name(name)
            
            if element and element.visible:
                return {
                    "found": True,
                    "element": element.to_dict(),
                }
            
            time.sleep(0.1)
        
        return {
            "found": False,
            "error": "Timeout waiting for element",
        }
    
    # ============================================================
    # 道具操作指令处理器
    # ============================================================
    
    def _handle_item_use(self, params: dict) -> dict:
        """使用道具
        
        参数:
            - slot_index: 道具槽索引
            - item_id: 道具 ID
        """
        # 方式1：通过槽位索引
        slot_index = params.get("slot_index")
        if slot_index is not None:
            ui_manager = self._get_ui_manager()
            if ui_manager:
                inventory = ui_manager.get_element("inventory_panel")
                if inventory and hasattr(inventory, 'get_slot'):
                    slot = inventory.get_slot(slot_index)
                    if slot:
                        slot.click()
                        return {"success": True, "slot_index": slot_index}
        
        # 方式2：通过道具 ID
        item_id = params.get("item_id")
        if item_id:
            if hasattr(self.game, 'use_item'):
                self.game.use_item(item_id)
                return {"success": True, "item_id": item_id}
        
        raise ValueError("Failed to use item")
    
    def _handle_item_get_info(self, params: dict) -> dict:
        """获取道具信息
        
        参数:
            - slot_index: 道具槽索引
            - item_id: 道具 ID
        """
        ui_manager = self._get_ui_manager()
        if not ui_manager:
            raise NotImplementedError("UI manager not available")
        
        slot_index = params.get("slot_index")
        item_id = params.get("item_id")
        
        if slot_index is not None:
            inventory = ui_manager.get_element("inventory_panel")
            if inventory and hasattr(inventory, 'get_slot'):
                slot = inventory.get_slot(slot_index)
                if slot:
                    return {
                        "slot_index": slot_index,
                        "item": slot.item,
                    }
        
        raise ValueError("Item not found")
    
    def _handle_item_equip(self, params: dict) -> dict:
        """装备道具"""
        item_id = params["item_id"]
        
        if hasattr(self.game, 'equip_item'):
            self.game.equip_item(item_id)
            return {"success": True}
        
        raise NotImplementedError("equip_item not implemented")
    
    def _handle_item_drop(self, params: dict) -> dict:
        """丢弃道具"""
        item_id = params["item_id"]
        
        if hasattr(self.game, 'drop_item'):
            self.game.drop_item(item_id)
            return {"success": True}
        
        raise NotImplementedError("drop_item not implemented")
    
    def _get_ui_manager(self):
        """获取 UI 管理器"""
        return getattr(self.game, 'ui_manager', None) or \
               getattr(self.game, 'ui', None)
