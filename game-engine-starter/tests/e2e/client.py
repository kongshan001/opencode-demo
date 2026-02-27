"""
测试客户端 - 连接游戏并发送测试指令
"""

import socket
import json
import uuid
import time
from typing import Any, Dict, Optional
from dataclasses import dataclass
from contextlib import contextmanager


@dataclass
class CommandResult:
    """指令执行结果"""
    id: str
    success: bool
    result: Any
    error: Optional[str]
    duration: float
    round_trip_time: float
    
    def __bool__(self):
        return self.success


class GameTestClient:
    """
    游戏测试客户端
    
    连接游戏 Socket 服务器并发送测试指令
    """
    
    def __init__(self, host: str = "localhost", port: int = 9876):
        self.host = host
        self.port = port
        self._socket: Optional[socket.socket] = None
    
    def connect(self, timeout: float = 5.0):
        """连接游戏"""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(timeout)
        self._socket.connect((self.host, self.port))
        print(f"[Client] Connected to {self.host}:{self.port}")
    
    def disconnect(self):
        """断开连接"""
        if self._socket:
            self._socket.close()
            self._socket = None
            print("[Client] Disconnected")
    
    def send_command(
        self,
        command_type: str,
        params: Dict[str, Any] = None,
        timeout: float = 5.0,
    ) -> CommandResult:
        """发送指令"""
        if self._socket is None:
            raise RuntimeError("Not connected")
        
        start_time = time.perf_counter()
        
        # 构建指令
        command = {
            "id": str(uuid.uuid4()),
            "type": command_type,
            "params": params or {},
            "timeout": timeout,
        }
        
        # 发送
        self._send_message(command)
        
        # 接收响应
        response = self._recv_message()
        
        round_trip_time = time.perf_counter() - start_time
        
        return CommandResult(
            id=response["id"],
            success=response["success"],
            result=response.get("result"),
            error=response.get("error"),
            duration=response.get("duration", 0),
            round_trip_time=round_trip_time,
        )
    
    def _send_message(self, message: dict):
        """发送消息（带长度前缀）"""
        data = json.dumps(message).encode('utf-8')
        length = len(data).to_bytes(4, 'big')
        self._socket.sendall(length + data)
    
    def _recv_message(self) -> dict:
        """接收消息（带长度前缀）"""
        length_data = self._socket.recv(4)
        length = int.from_bytes(length_data, 'big')
        
        data = b''
        while len(data) < length:
            chunk = self._socket.recv(min(4096, length - len(data)))
            if not chunk:
                raise ConnectionError("Connection closed")
            data += chunk
        
        return json.loads(data.decode('utf-8'))
    
    # ============================================================
    # 便捷方法
    # ============================================================
    
    def entity_create(self, entity_type: str = "Entity", components: list = None) -> CommandResult:
        """创建实体"""
        return self.send_command("entity.create", {
            "type": entity_type,
            "components": components or [],
        })
    
    def entity_get(self, entity_id: int) -> CommandResult:
        """获取实体"""
        return self.send_command("entity.get", {"entity_id": entity_id})
    
    def entity_list(self) -> CommandResult:
        """列出所有实体"""
        return self.send_command("entity.list")
    
    def component_get(self, entity_id: int, component_type: str) -> CommandResult:
        """获取组件"""
        return self.send_command("component.get", {
            "entity_id": entity_id,
            "component_type": component_type,
        })
    
    def component_set(self, entity_id: int, component_type: str, properties: dict) -> CommandResult:
        """设置组件属性"""
        return self.send_command("component.set", {
            "entity_id": entity_id,
            "component_type": component_type,
            "properties": properties,
        })
    
    def game_pause(self) -> CommandResult:
        """暂停游戏"""
        return self.send_command("game.pause")
    
    def game_resume(self) -> CommandResult:
        """恢复游戏"""
        return self.send_command("game.resume")
    
    def game_step(self, dt: float = 0.016) -> CommandResult:
        """单步执行"""
        return self.send_command("game.step", {"dt": dt})
    
    def state_get(self, key: str = None) -> CommandResult:
        """获取状态"""
        params = {"key": key} if key else {}
        return self.send_command("state.get", params)
    
    def state_set(self, key: str, value: Any) -> CommandResult:
        """设置状态"""
        return self.send_command("state.set", {"key": key, "value": value})
    
    def input_key(self, key: str, action: str = "tap") -> CommandResult:
        """模拟按键 (press/release/tap)"""
        return self.send_command("input.key", {"key": key, "action": action})
    
    def perf_fps(self) -> CommandResult:
        """获取 FPS"""
        return self.send_command("perf.fps")
    
    def render_count(self) -> CommandResult:
        """获取渲染次数"""
        return self.send_command("render.count")
    
    # 上下文管理
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False


@contextmanager
def game_client(host: str = "localhost", port: int = 9876):
    """便捷上下文管理器"""
    client = GameTestClient(host, port)
    client.connect()
    try:
        yield client
    finally:
        client.disconnect()
