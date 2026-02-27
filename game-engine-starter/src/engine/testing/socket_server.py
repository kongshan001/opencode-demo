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
