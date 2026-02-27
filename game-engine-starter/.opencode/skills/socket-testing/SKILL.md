---
name: socket-testing
description: 基于 Socket 通信的游戏自动化测试框架
license: MIT
metadata:
  category: testing
  type: e2e
---

## Socket 通信自动化测试

通过 Socket 建立测试框架与游戏的通信，实现 E2E 自动化测试。

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    E2E 测试架构                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐         Socket         ┌──────────────┐  │
│  │              │ ◄──────────────────────►│              │  │
│  │  测试框架    │    JSON 指令/响应       │   游戏进程   │  │
│  │  (pytest)    │                         │  (被测对象)  │  │
│  │              │                         │              │  │
│  └──────────────┘                         └──────────────┘  │
│        │                                        │           │
│        ▼                                        ▼           │
│  ┌──────────────┐                         ┌──────────────┐  │
│  │  断言/报告   │                         │  Socket 服务 │  │
│  └──────────────┘                         └──────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 一、游戏端 Socket 服务器

### 1. 服务器实现

```python
# src/engine/testing/socket_server.py
"""
游戏内嵌 Socket 服务器
用于接收测试指令并返回执行结果
"""

import socket
import json
import threading
import traceback
from typing import Callable, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class CommandType(Enum):
    """指令类型"""
    # 实体操作
    ENTITY_CREATE = "entity.create"
    ENTITY_GET = "entity.get"
    ENTITY_DELETE = "entity.delete"
    
    # 组件操作
    COMPONENT_GET = "component.get"
    COMPONENT_SET = "component.set"
    
    # 游戏控制
    GAME_PAUSE = "game.pause"
    GAME_RESUME = "game.resume"
    GAME_STEP = "game.step"
    GAME_SPEED = "game.speed"
    
    # 状态查询
    STATE_GET = "state.get"
    STATE_SET = "state.set"
    
    # 输入模拟
    INPUT_KEY = "input.key"
    INPUT_MOUSE = "input.mouse"
    
    # 渲染
    RENDER_CAPTURE = "render.capture"
    RENDER_COUNT = "render.count"
    
    # 性能
    PERF_FPS = "perf.fps"
    PERF_MEMORY = "perf.memory"
    
    # 自定义
    CUSTOM = "custom"


@dataclass
class TestCommand:
    """测试指令"""
    id: str
    type: str
    params: Dict[str, Any]
    timeout: float = 5.0


@dataclass
class TestResponse:
    """测试响应"""
    id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    duration: float = 0.0


class GameTestServer:
    """
    游戏内嵌测试服务器
    
    在游戏中启动，监听测试指令并执行
    """
    
    def __init__(self, game, host: str = "localhost", port: int = 9876):
        self.game = game
        self.host = host
        self.port = port
        
        self._socket: Optional[socket.socket] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        # 注册指令处理器
        self._handlers: Dict[str, Callable] = {
            CommandType.ENTITY_CREATE.value: self._handle_entity_create,
            CommandType.ENTITY_GET.value: self._handle_entity_get,
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
        """注册自定义指令处理器"""
        self._custom_handlers[command_type] = handler
    
    def start(self):
        """启动服务器"""
        if self._running:
            return
        
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.host, self.port))
        self._socket.listen(1)
        self._socket.settimeout(1.0)  # 允许优雅关闭
        
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        
        print(f"[TestServer] Listening on {self.host}:{self.port}")
    
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
                print(f"[TestServer] Connection from {addr}")
                
                with conn:
                    while self._running:
                        # 接收数据
                        data = self._recv_message(conn)
                        if not data:
                            break
                        
                        # 处理指令
                        response = self._handle_message(data)
                        
                        # 发送响应
                        self._send_message(conn, response)
                        
            except socket.timeout:
                continue
            except Exception as e:
                if self._running:
                    print(f"[TestServer] Error: {e}")
    
    def _recv_message(self, conn) -> Optional[dict]:
        """接收消息（带长度前缀）"""
        # 读取长度（4字节）
        length_data = conn.recv(4)
        if not length_data:
            return None
        
        length = int.from_bytes(length_data, 'big')
        
        # 读取数据
        data = b''
        while len(data) < length:
            chunk = conn.recv(min(4096, length - len(data)))
            if not chunk:
                return None
            data += chunk
        
        return json.loads(data.decode('utf-8'))
    
    def _send_message(self, conn, message: dict):
        """发送消息（带长度前缀）"""
        data = json.dumps(message).encode('utf-8')
        length = len(data).to_bytes(4, 'big')
        conn.sendall(length + data)
    
    def _handle_message(self, data: dict) -> dict:
        """处理消息"""
        import time
        
        command = TestCommand(
            id=data.get("id", ""),
            type=data.get("type", ""),
            params=data.get("params", {}),
            timeout=data.get("timeout", 5.0),
        )
        
        start_time = time.perf_counter()
        
        try:
            # 查找处理器
            handler = self._handlers.get(command.type)
            if handler is None:
                handler = self._custom_handlers.get(command.type)
            
            if handler is None:
                raise ValueError(f"Unknown command type: {command.type}")
            
            # 执行
            result = handler(command.params)
            
            duration = time.perf_counter() - start_time
            
            response = TestResponse(
                id=command.id,
                success=True,
                result=result,
                duration=duration,
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            response = TestResponse(
                id=command.id,
                success=False,
                error=f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}",
                duration=duration,
            )
        
        return {
            "id": response.id,
            "success": response.success,
            "result": response.result,
            "error": response.error,
            "duration": response.duration,
        }
    
    # ============================================================
    # 指令处理器
    # ============================================================
    
    def _handle_entity_create(self, params: dict) -> dict:
        """创建实体"""
        entity_type = params.get("type", "Entity")
        components = params.get("components", [])
        
        # 创建实体（根据你的引擎实现）
        entity = self.game.create_entity(entity_type)
        
        # 添加组件
        for comp_data in components:
            comp_type = comp_data["type"]
            comp_params = comp_data.get("params", {})
            entity.add_component(comp_type, **comp_params)
        
        return {"entity_id": entity.id}
    
    def _handle_entity_get(self, params: dict) -> dict:
        """获取实体信息"""
        entity_id = params["entity_id"]
        entity = self.game.get_entity(entity_id)
        
        if entity is None:
            raise ValueError(f"Entity not found: {entity_id}")
        
        return {
            "id": entity.id,
            "active": entity.is_active,
            "components": [
                {"type": type(c).__name__, "data": c.to_dict()}
                for c in entity.components.values()
            ]
        }
    
    def _handle_component_get(self, params: dict) -> dict:
        """获取组件"""
        entity_id = params["entity_id"]
        component_type = params["component_type"]
        
        entity = self.game.get_entity(entity_id)
        if entity is None:
            raise ValueError(f"Entity not found: {entity_id}")
        
        component = entity.get_component(component_type)
        if component is None:
            raise ValueError(f"Component not found: {component_type}")
        
        return component.to_dict()
    
    def _handle_component_set(self, params: dict) -> dict:
        """设置组件属性"""
        entity_id = params["entity_id"]
        component_type = params["component_type"]
        properties = params["properties"]
        
        entity = self.game.get_entity(entity_id)
        component = entity.get_component(component_type)
        
        for key, value in properties.items():
            setattr(component, key, value)
        
        return {"success": True}
    
    def _handle_game_pause(self, params: dict) -> dict:
        """暂停游戏"""
        self.game.pause()
        return {"paused": True}
    
    def _handle_game_resume(self, params: dict) -> dict:
        """恢复游戏"""
        self.game.resume()
        return {"paused": False}
    
    def _handle_game_step(self, params: dict) -> dict:
        """单步执行"""
        dt = params.get("dt", 0.016)
        self.game.step(dt)
        return {"stepped": True, "dt": dt}
    
    def _handle_state_get(self, params: dict) -> dict:
        """获取游戏状态"""
        key = params.get("key")
        
        if key:
            return {"value": self.game.get_state(key)}
        else:
            return self.game.get_full_state()
    
    def _handle_state_set(self, params: dict) -> dict:
        """设置游戏状态"""
        key = params["key"]
        value = params["value"]
        
        self.game.set_state(key, value)
        return {"success": True}
    
    def _handle_input_key(self, params: dict) -> dict:
        """模拟按键输入"""
        key = params["key"]
        action = params.get("action", "press")  # press, release, tap
        
        if action == "press":
            self.game.input.key_press(key)
        elif action == "release":
            self.game.input.key_release(key)
        elif action == "tap":
            self.game.input.key_tap(key)
        
        return {"success": True}
    
    def _handle_perf_fps(self, params: dict) -> dict:
        """获取 FPS"""
        return {
            "fps": self.game.fps_counter.fps,
            "frame_time": self.game.fps_counter.frame_time,
        }
    
    def _handle_render_count(self, params: dict) -> dict:
        """获取渲染调用次数"""
        return {
            "draw_calls": self.game.renderer.draw_count,
            "batch_calls": self.game.renderer.batch_count,
        }


# ============================================================
# 游戏集成示例
# ============================================================

class GameWithTesting:
    """支持测试的游戏基类"""
    
    def __init__(self):
        # ... 初始化游戏 ...
        self.test_server = GameTestServer(self)
    
    def run(self):
        """运行游戏"""
        # 启动测试服务器
        self.test_server.start()
        
        try:
            # 游戏主循环
            while self.is_running:
                self.update()
                self.render()
        finally:
            # 停止测试服务器
            self.test_server.stop()
    
    # 游戏需要实现的方法
    def create_entity(self, entity_type: str):
        pass
    
    def get_entity(self, entity_id: int):
        pass
    
    def pause(self):
        pass
    
    def resume(self):
        pass
    
    def step(self, dt: float):
        pass
```

### 2. 游戏启动器

```python
# src/engine/testing/launcher.py
"""
游戏启动器
管理游戏进程的生命周期
"""

import subprocess
import time
import socket
import json
import os
import signal
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class GameProcess:
    """游戏进程信息"""
    process: subprocess.Popen
    host: str
    port: int
    startup_time: float


class GameLauncher:
    """
    游戏启动器
    
    负责启动游戏进程并建立通信
    """
    
    def __init__(
        self,
        game_path: str,
        host: str = "localhost",
        port: int = 9876,
        startup_timeout: float = 10.0,
    ):
        self.game_path = game_path
        self.host = host
        self.port = port
        self.startup_timeout = startup_timeout
        
        self._process: Optional[GameProcess] = None
    
    def start(self, args: List[str] = None, env: dict = None) -> GameProcess:
        """启动游戏"""
        if self._process is not None:
            raise RuntimeError("Game already running")
        
        # 构建命令
        cmd = ["python", self.game_path]
        if args:
            cmd.extend(args)
        
        # 添加测试模式参数
        cmd.extend(["--test-mode", "--test-port", str(self.port)])
        
        # 环境变量
        full_env = os.environ.copy()
        if env:
            full_env.update(env)
        
        # 启动进程
        start_time = time.perf_counter()
        process = subprocess.Popen(
            cmd,
            env=full_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        # 等待连接就绪
        self._wait_for_ready(start_time)
        
        self._process = GameProcess(
            process=process,
            host=self.host,
            port=self.port,
            startup_time=time.perf_counter() - start_time,
        )
        
        return self._process
    
    def _wait_for_ready(self, start_time: float):
        """等待游戏就绪"""
        while time.perf_counter() - start_time < self.startup_timeout:
            try:
                # 尝试连接
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                sock.connect((self.host, self.port))
                sock.close()
                return  # 连接成功
            except (socket.error, ConnectionRefusedError):
                time.sleep(0.1)
        
        raise TimeoutError(f"Game did not start within {self.startup_timeout}s")
    
    def stop(self):
        """停止游戏"""
        if self._process is None:
            return
        
        # 优雅关闭
        self._process.process.terminate()
        
        try:
            self._process.process.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            # 强制关闭
            self._process.process.kill()
            self._process.process.wait()
        
        self._process = None
    
    def is_running(self) -> bool:
        """检查游戏是否运行"""
        if self._process is None:
            return False
        return self._process.process.poll() is None
    
    def get_output(self) -> tuple:
        """获取游戏输出"""
        if self._process is None:
            return "", ""
        
        # 非阻塞读取
        import select
        
        stdout = ""
        stderr = ""
        
        if self._process.process.stdout:
            readable, _, _ = select.select([self._process.process.stdout], [], [], 0)
            if readable:
                stdout = self._process.process.stdout.read()
        
        if self._process.process.stderr:
            readable, _, _ = select.select([self._process.process.stderr], [], [], 0)
            if readable:
                stderr = self._process.process.stderr.read()
        
        return stdout, stderr
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False
```

## 二、测试客户端

### 1. 客户端实现

```python
# tests/e2e/client.py
"""
测试客户端
用于连接游戏并发送测试指令
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


class GameTestClient:
    """
    游戏测试客户端
    
    连接游戏服务器并发送测试指令
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
    
    def disconnect(self):
        """断开连接"""
        if self._socket:
            self._socket.close()
            self._socket = None
    
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
        """发送消息"""
        data = json.dumps(message).encode('utf-8')
        length = len(data).to_bytes(4, 'big')
        self._socket.sendall(length + data)
    
    def _recv_message(self) -> dict:
        """接收消息"""
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
        """模拟按键"""
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
```

### 2. Pytest Fixture

```python
# tests/e2e/conftest.py
"""
E2E 测试配置
"""

import pytest
from tests.e2e.client import GameTestClient, GameLauncher
from tests.e2e.launcher import GameLauncher


@pytest.fixture(scope="session")
def game_launcher():
    """游戏启动器 fixture"""
    launcher = GameLauncher(
        game_path="main.py",  # 你的游戏入口
        port=9876,
    )
    yield launcher
    launcher.stop()


@pytest.fixture(scope="function")
def game_process(game_launcher):
    """每个测试启动独立游戏进程"""
    game_launcher.start()
    yield game_launcher
    game_launcher.stop()


@pytest.fixture(scope="function")
def game_client(game_process):
    """测试客户端 fixture"""
    with GameTestClient(port=9876) as client:
        yield client


@pytest.fixture(scope="function")
def paused_game(game_client):
    """暂停的游戏（用于确定性测试）"""
    game_client.game_pause()
    yield game_client
    game_client.game_resume()
```

## 三、E2E 测试用例

### 1. 基础测试

```python
# tests/e2e/test_game_basic.py
"""
基础 E2E 测试
"""

import pytest
from tests.e2e.client import GameTestClient


class TestGameBasic:
    """游戏基础功能测试"""
    
    def test_game_starts(self, game_client):
        """测试游戏启动"""
        result = game_client.state_get()
        assert result.success
    
    def test_fps_reporting(self, game_client):
        """测试 FPS 报告"""
        result = game_client.perf_fps()
        
        assert result.success
        assert "fps" in result.result
        assert result.result["fps"] > 0
    
    def test_entity_lifecycle(self, game_client):
        """测试实体生命周期"""
        # 创建实体
        create_result = game_client.entity_create("Player")
        assert create_result.success
        
        entity_id = create_result.result["entity_id"]
        
        # 获取实体
        get_result = game_client.entity_get(entity_id)
        assert get_result.success
        assert get_result.result["id"] == entity_id
    
    def test_component_manipulation(self, game_client):
        """测试组件操作"""
        # 创建实体
        entity = game_client.entity_create(
            components=[{"type": "Transform", "params": {"x": 0, "y": 0}}]
        )
        entity_id = entity.result["entity_id"]
        
        # 获取组件
        transform = game_client.component_get(entity_id, "Transform")
        assert transform.success
        assert transform.result["x"] == 0
        
        # 修改组件
        game_client.component_set(entity_id, "Transform", {"x": 100, "y": 200})
        
        # 验证修改
        transform = game_client.component_get(entity_id, "Transform")
        assert transform.result["x"] == 100
        assert transform.result["y"] == 200
```

### 2. 游戏逻辑测试

```python
# tests/e2e/test_game_logic.py
"""
游戏逻辑 E2E 测试
"""

import pytest


class TestGameLogic:
    """游戏逻辑测试"""
    
    def test_player_movement(self, paused_game):
        """测试玩家移动"""
        client = paused_game
        
        # 创建玩家
        result = client.entity_create(
            "Player",
            components=[
                {"type": "Transform", "params": {"x": 0, "y": 0}},
                {"type": "Velocity", "params": {"dx": 10, "dy": 0}},
            ]
        )
        player_id = result.result["entity_id"]
        
        # 执行一帧
        client.game_step(dt=1.0)
        
        # 验证位置
        transform = client.component_get(player_id, "Transform")
        assert transform.result["x"] == 10
    
    def test_collision_detection(self, paused_game):
        """测试碰撞检测"""
        client = paused_game
        
        # 创建两个重叠的实体
        entity1 = client.entity_create(
            components=[
                {"type": "Transform", "params": {"x": 0, "y": 0}},
                {"type": "BoundingBox", "params": {"width": 10, "height": 10}},
            ]
        )
        
        entity2 = client.entity_create(
            components=[
                {"type": "Transform", "params": {"x": 5, "y": 5}},
                {"type": "BoundingBox", "params": {"width": 10, "height": 10}},
            ]
        )
        
        # 执行碰撞检测
        result = client.send_command("collision.check", {
            "entity1_id": entity1.result["entity_id"],
            "entity2_id": entity2.result["entity_id"],
        })
        
        assert result.success
        assert result.result["colliding"] == True
    
    def test_game_state(self, game_client):
        """测试游戏状态"""
        # 设置状态
        game_client.state_set("score", 100)
        
        # 获取状态
        result = game_client.state_get("score")
        assert result.result["value"] == 100


class TestInput:
    """输入测试"""
    
    def test_keyboard_input(self, paused_game):
        """测试键盘输入"""
        client = paused_game
        
        # 模拟按键
        result = client.input_key("SPACE", action="tap")
        assert result.success
        
        # 验证输入被处理（根据你的游戏逻辑）
        state = client.state_get("last_input")
        assert state.result["value"] == "SPACE"
    
    def test_continuous_input(self, paused_game):
        """测试持续输入"""
        client = paused_game
        
        # 创建可移动实体
        entity = client.entity_create(
            components=[
                {"type": "Transform", "params": {"x": 0, "y": 0}},
                {"type": "InputController", "params": {}},
            ]
        )
        entity_id = entity.result["entity_id"]
        
        # 按住按键
        client.input_key("RIGHT", action="press")
        
        # 执行多帧
        for _ in range(10):
            client.game_step(dt=0.1)
        
        # 释放按键
        client.input_key("RIGHT", action="release")
        
        # 验证移动
        transform = client.component_get(entity_id, "Transform")
        assert transform.result["x"] > 0
```

### 3. 性能测试

```python
# tests/e2e/test_performance.py
"""
性能 E2E 测试
"""

import pytest
import time


class TestPerformance:
    """性能测试"""
    
    def test_frame_time_stability(self, game_client):
        """测试帧时间稳定性"""
        frame_times = []
        
        for _ in range(100):
            start = time.perf_counter()
            game_client.game_step(dt=0.016)
            elapsed = time.perf_counter() - start
            frame_times.append(elapsed)
        
        import statistics
        avg = statistics.mean(frame_times)
        std = statistics.stdev(frame_times)
        max_time = max(frame_times)
        
        print(f"\n帧时间统计:")
        print(f"  平均: {avg * 1000:.2f}ms")
        print(f"  标准差: {std * 1000:.2f}ms")
        print(f"  最大: {max_time * 1000:.2f}ms")
        
        # 确保帧时间稳定
        assert avg < 0.02  # 平均小于 20ms
        assert std < 0.005  # 标准差小于 5ms
    
    def test_entity_scalability(self, game_client):
        """测试实体扩展性"""
        # 创建不同数量的实体
        for count in [100, 500, 1000, 2000]:
            # 清除旧实体
            game_client.send_command("entity.clear_all")
            
            # 创建新实体
            start = time.perf_counter()
            for _ in range(count):
                game_client.entity_create()
            create_time = time.perf_counter() - start
            
            # 执行一帧
            start = time.perf_counter()
            game_client.game_step(dt=0.016)
            update_time = time.perf_counter() - start
            
            # 获取 FPS
            fps = game_client.perf_fps()
            
            print(f"\n{count} 实体:")
            print(f"  创建时间: {create_time * 1000:.2f}ms")
            print(f"  更新时间: {update_time * 1000:.2f}ms")
            print(f"  FPS: {fps.result['fps']:.1f}")
            
            # 验证性能
            assert update_time < 0.1  # 更新时间小于 100ms
    
    def test_render_performance(self, game_client):
        """测试渲染性能"""
        # 创建大量实体
        for _ in range(1000):
            game_client.entity_create(
                components=[{"type": "Sprite", "params": {"texture": "test.png"}}]
            )
        
        # 执行渲染
        game_client.game_step(dt=0.016)
        
        # 获取渲染统计
        result = game_client.render_count()
        
        print(f"\n渲染统计:")
        print(f"  Draw calls: {result.result['draw_calls']}")
        print(f"  Batch calls: {result.result['batch_calls']}")
```

## 四、测试运行器

```python
# tests/e2e/runner.py
"""
E2E 测试运行器
"""

import sys
import pytest
from pathlib import Path


def run_e2e_tests(
    game_path: str,
    markers: list = None,
    verbose: bool = True,
    capture_output: bool = False,
):
    """运行 E2E 测试"""
    
    # 设置环境变量
    import os
    os.environ["GAME_PATH"] = game_path
    
    # 构建 pytest 参数
    args = [str(Path(__file__).parent)]
    
    if verbose:
        args.append("-v")
    
    if markers:
        args.extend(["-m", " and ".join(markers)])
    
    if not capture_output:
        args.append("-s")
    
    # 添加自定义选项
    args.extend([
        "--tb=short",
        "--durations=10",
    ])
    
    # 运行测试
    return pytest.main(args)


if __name__ == "__main__":
    game_path = sys.argv[1] if len(sys.argv) > 1 else "main.py"
    sys.exit(run_e2e_tests(game_path))
```

## 五、使用方法

### 1. 游戏端集成

```python
# main.py
from engine.game import Game
from engine.testing.socket_server import GameTestServer

def main():
    game = Game()
    
    # 如果是测试模式，启动测试服务器
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-mode", action="store_true")
    parser.add_argument("--test-port", type=int, default=9876)
    args = parser.parse_args()
    
    if args.test_mode:
        game.test_server = GameTestServer(game, port=args.test_port)
        game.test_server.start()
    
    try:
        game.run()
    finally:
        if args.test_mode:
            game.test_server.stop()

if __name__ == "__main__":
    main()
```

### 2. 运行测试

```bash
# 运行所有 E2E 测试
pytest tests/e2e -v

# 运行特定测试
pytest tests/e2e/test_game_logic.py -v

# 使用启动器
python tests/e2e/runner.py main.py
```

### 3. CI/CD 集成

```yaml
# .github/workflows/e2e.yml
- name: Run E2E tests
  run: |
    python tests/e2e/runner.py main.py
  
- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: e2e-results
    path: test-results/
```
