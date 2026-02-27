# Socket 通信自动化测试框架（完整版）

基于 Socket 通信的游戏 E2E 自动化测试框架，支持 exe 启动。

## 架构设计

```
┌──────────────────────────────────────────────────────────────────┐
│                      自动化测试流程                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   pytest                                                          │
│     │                                                             │
│     ▼                                                             │
│   ┌─────────────┐      写入配置文件           ┌─────────────┐     │
│   │ GameLauncher│ ──────────────────────────► │ test_mode   │     │
│   │             │      test_mode.json         │   .json     │     │
│   └─────────────┘                              └─────────────┘     │
│         │                                             │            │
│         │ subprocess.Popen                            │            │
│         ▼                                             ▼            │
│   ┌─────────────┐      启动 exe              ┌─────────────┐       │
│   │ mygame.exe  │ ◄─────────────────────────│ 读取配置    │       │
│   │             │                            │ 启动Socket  │       │
│   └─────────────┘                            └─────────────┘       │
│         │                                                             │
│         ▼                                                             │
│   ┌─────────────┐      Socket 连接           ┌─────────────┐       │
│   │GameTestClient│ ◄────────────────────────►│GameTestServer│      │
│   │             │      JSON 指令/响应        │             │       │
│   └─────────────┘                            └─────────────┘       │
│         │                                                             │
│         ▼                                                             │
│   执行测试用例 → 断言验证 → 删除配置 → 关闭 exe                      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## 一、游戏端集成

### 1.1 Socket 服务器实现

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
    ENTITY_LIST = "entity.list"
    
    # 组件操作
    COMPONENT_GET = "component.get"
    COMPONENT_SET = "component.set"
    
    # 游戏控制
    GAME_PAUSE = "game.pause"
    GAME_RESUME = "game.resume"
    GAME_STEP = "game.step"
    GAME_SPEED = "game.speed"
    GAME_RESET = "game.reset"
    
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
    
    # 场景
    SCENE_LOAD = "scene.load"
    SCENE_CURRENT = "scene.current"


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
        self._socket.settimeout(1.0)
        
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
        """接收消息（带长度前缀）"""
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
            handler = self._handlers.get(command.type)
            if handler is None:
                handler = self._custom_handlers.get(command.type)
            
            if handler is None:
                raise ValueError(f"Unknown command type: {command.type}")
            
            result = handler(command.params)
            duration = time.perf_counter() - start_time
            
            return {
                "id": command.id,
                "success": True,
                "result": result,
                "error": None,
                "duration": duration,
            }
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            return {
                "id": command.id,
                "success": False,
                "result": None,
                "error": f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}",
                "duration": duration,
            }
    
    # ============================================================
    # 指令处理器（需要根据你的游戏实现修改）
    # ============================================================
    
    def _handle_entity_create(self, params: dict) -> dict:
        """创建实体"""
        entity_type = params.get("type", "Entity")
        components = params.get("components", [])
        
        # TODO: 根据你的游戏实现
        entity = self.game.create_entity(entity_type)
        
        for comp_data in components:
            comp_type = comp_data["type"]
            comp_params = comp_data.get("params", {})
            entity.add_component(comp_type, **comp_params)
        
        return {"entity_id": entity.id}
    
    def _handle_entity_get(self, params: dict) -> dict:
        """获取实体"""
        entity_id = params["entity_id"]
        entity = self.game.get_entity(entity_id)
        
        if entity is None:
            raise ValueError(f"Entity not found: {entity_id}")
        
        return {
            "id": entity.id,
            "active": entity.is_active,
            "components": []
        }
    
    def _handle_entity_list(self, params: dict) -> dict:
        """列出所有实体"""
        entities = self.game.get_all_entities()
        return {
            "count": len(entities),
            "entities": [{"id": e.id, "active": e.is_active} for e in entities]
        }
    
    def _handle_component_get(self, params: dict) -> dict:
        """获取组件"""
        entity_id = params["entity_id"]
        component_type = params["component_type"]
        
        entity = self.game.get_entity(entity_id)
        component = entity.get_component(component_type)
        
        if component is None:
            raise ValueError(f"Component not found: {component_type}")
        
        # TODO: 返回组件数据
        return component.to_dict() if hasattr(component, 'to_dict') else {}
    
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
            return {"value": getattr(self.game, key, None)}
        else:
            return self.game.get_state()
    
    def _handle_state_set(self, params: dict) -> dict:
        """设置游戏状态"""
        key = params["key"]
        value = params["value"]
        setattr(self.game, key, value)
        return {"success": True}
    
    def _handle_input_key(self, params: dict) -> dict:
        """模拟按键"""
        key = params["key"]
        action = params.get("action", "tap")
        
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
            "fps": getattr(self.game, 'fps', 0),
            "frame_time": getattr(self.game, 'frame_time', 0),
        }
    
    def _handle_render_count(self, params: dict) -> dict:
        """获取渲染调用次数"""
        return {
            "draw_calls": getattr(self.game.renderer, 'draw_count', 0),
        }
```

### 1.2 配置文件读取器

```python
# src/engine/testing/config.py
"""
测试模式配置读取器
"""

import json
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class TestModeConfig:
    """测试模式配置"""
    enabled: bool = False
    port: int = 9876
    host: str = "localhost"
    auto_start: bool = True
    timeout: float = 10.0
    
    @classmethod
    def from_file(cls, config_path: str = "test_mode.json") -> "TestModeConfig":
        """从配置文件读取"""
        if not os.path.exists(config_path):
            return cls()
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return cls(
                enabled=data.get("enabled", True),
                port=data.get("port", 9876),
                host=data.get("host", "localhost"),
                auto_start=data.get("auto_start", True),
                timeout=data.get("timeout", 10.0),
            )
        except Exception as e:
            print(f"[TestConfig] Error reading config: {e}")
            return cls()
    
    @classmethod
    def from_env(cls) -> "TestModeConfig":
        """从环境变量读取"""
        enabled = os.environ.get("GAME_TEST_MODE", "0") == "1"
        port = int(os.environ.get("GAME_TEST_PORT", "9876"))
        host = os.environ.get("GAME_TEST_HOST", "localhost")
        
        return cls(enabled=enabled, port=port, host=host)
```

### 1.3 游戏集成代码

```python
# main.py 或你的游戏入口文件
"""
游戏入口 - 集成测试服务器
"""

from engine.game import Game
from engine.testing.socket_server import GameTestServer
from engine.testing.config import TestModeConfig


def main():
    # 创建游戏
    game = Game()
    
    # 检查测试模式（配置文件优先，然后是环境变量）
    config = TestModeConfig.from_file()
    if not config.enabled:
        config = TestModeConfig.from_env()
    
    # 如果是测试模式，启动 Socket 服务器
    test_server = None
    if config.enabled:
        print(f"[Game] Test mode enabled, starting server on port {config.port}")
        test_server = GameTestServer(game, port=config.port)
        test_server.start()
    
    try:
        # 游戏主循环
        game.run()
    finally:
        # 清理
        if test_server:
            test_server.stop()
        
        # 删除配置文件（可选）
        import os
        if os.path.exists("test_mode.json"):
            try:
                os.remove("test_mode.json")
            except:
                pass


if __name__ == "__main__":
    main()
```

### 1.4 打包 exe

```bash
# 使用 PyInstaller 打包
pyinstaller --onefile --name mygame main.py

# 生成的 exe 在 dist/mygame.exe
```

---

## 二、测试端实现

### 2.1 游戏启动器

```python
# tests/e2e/launcher.py
"""
游戏启动器 - 通过配置文件启动 exe
"""

import subprocess
import socket
import time
import json
import os
import psutil
from typing import Optional
from dataclasses import dataclass


@dataclass
class GameProcess:
    """游戏进程信息"""
    process: subprocess.Popen
    pid: int
    port: int
    startup_time: float


class GameLauncher:
    """
    游戏启动器
    
    通过配置文件方式启动 exe
    """
    
    def __init__(
        self,
        exe_path: str,
        port: int = 9876,
        work_dir: str = None,
        startup_timeout: float = 30.0,
    ):
        """
        Args:
            exe_path: exe 文件路径，如 "D:/games/mygame.exe"
            port: Socket 端口
            work_dir: 工作目录（配置文件会写到这里）
            startup_timeout: 启动超时时间
        """
        self.exe_path = exe_path
        self.port = port
        self.work_dir = work_dir or os.path.dirname(exe_path)
        self.startup_timeout = startup_timeout
        
        self._process: Optional[GameProcess] = None
        self._config_file = os.path.join(self.work_dir, "test_mode.json")
    
    def start(self) -> GameProcess:
        """启动游戏"""
        if self._process is not None:
            raise RuntimeError("Game already running")
        
        # 1. 写入配置文件
        self._write_config()
        
        # 2. 启动 exe
        start_time = time.perf_counter()
        
        self._process = subprocess.Popen(
            [self.exe_path],
            cwd=self.work_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        # 3. 等待 Socket 就绪
        self._wait_for_ready()
        
        startup_time = time.perf_counter() - start_time
        
        return GameProcess(
            process=self._process,
            pid=self._process.pid,
            port=self.port,
            startup_time=startup_time,
        )
    
    def _write_config(self):
        """写入测试配置文件"""
        config = {
            "enabled": True,
            "port": self.port,
            "host": "localhost",
            "auto_start": True,
            "timeout": self.startup_timeout,
        }
        
        with open(self._config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        
        print(f"[Launcher] Config written to {self._config_file}")
    
    def _wait_for_ready(self):
        """等待 Socket 服务就绪"""
        print(f"[Launcher] Waiting for game to start on port {self.port}...")
        
        start = time.perf_counter()
        while time.perf_counter() - start < self.startup_timeout:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                sock.connect(("localhost", self.port))
                sock.close()
                print(f"[Launcher] Game ready! ({time.perf_counter() - start:.2f}s)")
                return
            except:
                time.sleep(0.1)
        
        # 超时，打印错误信息
        if self._process:
            stdout, stderr = self._process.communicate(timeout=1)
            print(f"[Launcher] stdout: {stdout.decode()}")
            print(f"[Launcher] stderr: {stderr.decode()}")
        
        raise TimeoutError(f"Game did not start within {self.startup_timeout}s")
    
    def stop(self):
        """停止游戏"""
        if self._process is None:
            return
        
        print("[Launcher] Stopping game...")
        
        # 1. 尝试优雅关闭
        self._process.terminate()
        
        try:
            self._process.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            # 2. 强制关闭
            print("[Launcher] Force killing game...")
            self._process.kill()
            self._process.wait()
        
        # 3. 清理子进程
        try:
            parent = psutil.Process(self._process.pid)
            for child in parent.children(recursive=True):
                child.kill()
        except:
            pass
        
        # 4. 删除配置文件
        if os.path.exists(self._config_file):
            try:
                os.remove(self._config_file)
                print(f"[Launcher] Config file removed")
            except:
                pass
        
        self._process = None
        print("[Launcher] Game stopped")
    
    def is_running(self) -> bool:
        """检查游戏是否运行"""
        if self._process is None:
            return False
        return self._process.poll() is None
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False
```

### 2.2 测试客户端

```python
# tests/e2e/client.py
"""
测试客户端 - 连接游戏并发送指令
"""

import socket
import json
import uuid
import time
from typing import Any, Dict, Optional
from dataclasses import dataclass


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
        
        command = {
            "id": str(uuid.uuid4()),
            "type": command_type,
            "params": params or {},
            "timeout": timeout,
        }
        
        self._send_message(command)
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
        """模拟按键"""
        return self.send_command("input.key", {"key": key, "action": action})
    
    def perf_fps(self) -> CommandResult:
        """获取 FPS"""
        return self.send_command("perf.fps")
    
    def render_count(self) -> CommandResult:
        """获取渲染次数"""
        return self.send_command("render.count")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False
```

### 2.3 Pytest 配置

```python
# tests/e2e/conftest.py
"""
E2E 测试配置
"""

import pytest
import os
from tests.e2e.launcher import GameLauncher
from tests.e2e.client import GameTestClient


# ============================================================
# 配置区 - 根据你的项目修改
# ============================================================

# exe 文件路径
EXE_PATH = r"D:\mygame\mygame.exe"  # ← 改成你的 exe 路径

# 或者从环境变量读取
# EXE_PATH = os.environ.get("GAME_EXE_PATH", r"D:\mygame\mygame.exe")

# Socket 端口
PORT = 9876

# 启动超时
STARTUP_TIMEOUT = 30.0


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(scope="session")
def game_launcher():
    """游戏启动器（session 级别，所有测试共享）"""
    return GameLauncher(
        exe_path=EXE_PATH,
        port=PORT,
        startup_timeout=STARTUP_TIMEOUT,
    )


@pytest.fixture(scope="function")
def game_process(game_launcher):
    """每个测试启动独立游戏进程"""
    process = game_launcher.start()
    yield process
    game_launcher.stop()


@pytest.fixture(scope="function")
def game_client(game_process):
    """测试客户端（自动连接）"""
    with GameTestClient(port=PORT) as client:
        yield client


@pytest.fixture(scope="function")
def paused_game(game_client):
    """暂停的游戏（用于确定性测试）"""
    game_client.game_pause()
    yield game_client
    game_client.game_resume()
```

---

## 三、测试用例示例

### 3.1 基础测试

```python
# tests/e2e/test_basic.py
"""
基础 E2E 测试
"""

import pytest


class TestGameBasic:
    """游戏基础功能测试"""
    
    def test_game_starts(self, game_client):
        """测试：游戏能启动"""
        result = game_client.state_get()
        assert result.success, f"Failed: {result.error}"
    
    def test_fps_reporting(self, game_client):
        """测试：FPS 报告正常"""
        result = game_client.perf_fps()
        
        assert result.success
        assert "fps" in result.result
        assert result.result["fps"] >= 0
    
    def test_entity_list_empty(self, game_client):
        """测试：初始无实体"""
        result = game_client.entity_list()
        
        assert result.success
        # 根据你的游戏逻辑调整
        # assert result.result["count"] == 0


class TestEntity:
    """实体测试"""
    
    def test_entity_create(self, game_client):
        """测试：创建实体"""
        result = game_client.entity_create("Player")
        
        assert result.success
        assert "entity_id" in result.result
    
    def test_entity_get(self, game_client):
        """测试：获取实体"""
        # 创建实体
        create_result = game_client.entity_create("Player")
        entity_id = create_result.result["entity_id"]
        
        # 获取实体
        get_result = game_client.entity_get(entity_id)
        
        assert get_result.success
        assert get_result.result["id"] == entity_id
    
    def test_component_get_set(self, game_client):
        """测试：组件操作"""
        # 创建带组件的实体
        result = game_client.entity_create(
            "Player",
            components=[
                {"type": "Transform", "params": {"x": 0, "y": 0}}
            ]
        )
        entity_id = result.result["entity_id"]
        
        # 获取组件
        transform = game_client.component_get(entity_id, "Transform")
        assert transform.success
        assert transform.result["x"] == 0
        
        # 设置组件
        game_client.component_set(entity_id, "Transform", {"x": 100, "y": 200})
        
        # 验证
        transform = game_client.component_get(entity_id, "Transform")
        assert transform.result["x"] == 100
        assert transform.result["y"] == 200
```

### 3.2 游戏逻辑测试

```python
# tests/e2e/test_game_logic.py
"""
游戏逻辑测试
"""

import pytest


class TestMovement:
    """移动测试"""
    
    def test_player_moves_right(self, paused_game):
        """测试：玩家向右移动"""
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
        
        # 执行 1 秒
        client.game_step(dt=1.0)
        
        # 验证位置
        transform = client.component_get(player_id, "Transform")
        assert transform.result["x"] == 10
    
    def test_input_key_movement(self, paused_game):
        """测试：按键控制移动"""
        client = paused_game
        
        # 创建可控制的玩家
        result = client.entity_create(
            "Player",
            components=[
                {"type": "Transform", "params": {"x": 0, "y": 0}},
                {"type": "InputController", "params": {}},
            ]
        )
        player_id = result.result["entity_id"]
        
        # 按下右键
        client.input_key("RIGHT", action="press")
        
        # 执行 10 帧
        for _ in range(10):
            client.game_step(dt=0.1)
        
        # 释放按键
        client.input_key("RIGHT", action="release")
        
        # 验证移动
        transform = client.component_get(player_id, "Transform")
        assert transform.result["x"] > 0


class TestGameState:
    """游戏状态测试"""
    
    def test_state_set_get(self, game_client):
        """测试：状态读写"""
        # 设置状态
        client.state_set("score", 100)
        
        # 获取状态
        result = client.state_get("score")
        
        assert result.success
        assert result.result["value"] == 100
```

---

## 四、运行测试

### 4.1 运行命令

```bash
# 运行所有 E2E 测试
pytest tests/e2e -v

# 运行特定测试文件
pytest tests/e2e/test_basic.py -v

# 运行特定测试
pytest tests/e2e/test_basic.py::TestGameBasic::test_game_starts -v

# 带日志输出
pytest tests/e2e -v -s

# 失败时停止
pytest tests/e2e -v -x
```

### 4.2 输出示例

```
$ pytest tests/e2e/test_basic.py -v

================ test session starts ================
[Launcher] Config written to D:\mygame\test_mode.json
[Launcher] Waiting for game to start on port 9876...
[Launcher] Game ready! (2.34s)
[Client] Connected to localhost:9876

tests/e2e/test_basic.py::TestGameBasic::test_game_starts 
  [Client] send: entity.create
  [Client] recv: {"success": true}
  PASSED

tests/e2e/test_basic.py::TestGameBasic::test_fps_reporting 
  [Client] send: perf.fps
  [Client] recv: {"success": true, "result": {"fps": 60}}
  PASSED

[Client] Disconnected
[Launcher] Stopping game...
[Launcher] Config file removed
[Launcher] Game stopped

================ 2 passed in 5.67s ================
```

---

## 五、CI/CD 集成

### 5.1 GitHub Actions

```yaml
# .github/workflows/e2e.yml
name: E2E Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  e2e-tests:
    runs-on: windows-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pytest psutil
      
      - name: Run E2E tests
        env:
          GAME_EXE_PATH: ${{ github.workspace }}/dist/mygame.exe
        run: |
          pytest tests/e2e -v --tb=short
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: e2e-results
          path: test-results/
```

---

## 六、故障排查

### 6.1 游戏无法启动

```python
# 检查 exe 路径
import os
print(os.path.exists(r"D:\mygame\mygame.exe"))

# 检查端口占用
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('localhost', 9876))
print(f"Port 9876: {'in use' if result == 0 else 'free'}")
sock.close()
```

### 6.2 连接超时

```python
# 增加超时时间
launcher = GameLauncher(
    exe_path=EXE_PATH,
    startup_timeout=60.0,  # 60秒
)
```

### 6.3 进程无法关闭

```python
# 强制关闭所有相关进程
import psutil
import os

def kill_game_processes():
    for proc in psutil.process_iter(['pid', 'name']):
        if 'mygame' in proc.info['name'].lower():
            proc.kill()
```

---

## 七、完整目录结构

```
your-game/
├── src/
│   └── engine/
│       └── testing/
│           ├── socket_server.py    # Socket 服务器
│           └── config.py           # 配置读取器
├── tests/
│   └── e2e/
│       ├── conftest.py             # Pytest 配置
│       ├── launcher.py             # 游戏启动器
│       ├── client.py               # 测试客户端
│       ├── test_basic.py           # 基础测试
│       └── test_game_logic.py      # 逻辑测试
├── main.py                          # 游戏入口
├── pyproject.toml                   # 项目配置
└── README.md
```
