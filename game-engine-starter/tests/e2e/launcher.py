"""
游戏启动器 - 通过配置文件方式启动 exe
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
    host: str
    port: int
    startup_time: float


class GameLauncher:
    """
    游戏启动器
    
    通过配置文件方式启动 exe，管理游戏生命周期
    """
    
    def __init__(
        self,
        exe_path: str,
        port: int = 9876,
        host: str = "localhost",
        startup_timeout: float = 30.0,
        config_filename: str = "test_mode.json",
    ):
        self.exe_path = exe_path
        self.port = port
        self.host = host
        self.startup_timeout = startup_timeout
        self.config_filename = config_filename
        
        self._process: Optional[GameProcess] = None
        self._config_path: Optional[str] = None
    
    def start(self) -> GameProcess:
        """启动游戏"""
        if self._process is not None:
            raise RuntimeError("Game already running")
        
        # 验证 exe 路径
        if not os.path.exists(self.exe_path):
            raise FileNotFoundError(f"Game exe not found: {self.exe_path}")
        
        # 1. 写入配置文件
        self._write_config()
        
        # 2. 启动 exe
        start_time = time.perf_counter()
        
        try:
            process = subprocess.Popen(
                [self.exe_path],
                cwd=os.path.dirname(self.exe_path) or ".",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            self._remove_config()
            raise RuntimeError(f"Failed to start game: {e}")
        
        # 3. 等待 Socket 就绪
        try:
            self._wait_for_ready(start_time)
        except TimeoutError:
            process.terminate()
            self._remove_config()
            raise
        
        startup_time = time.perf_counter() - start_time
        
        self._process = GameProcess(
            process=process,
            host=self.host,
            port=self.port,
            startup_time=startup_time,
        )
        
        print(f"[Launcher] Game started (took {startup_time:.2f}s)")
        return self._process
    
    def _write_config(self):
        """写入测试模式配置文件"""
        config = {
            "enabled": True,
            "port": self.port,
            "host": self.host,
            "auto_start": True,
            "timeout": self.startup_timeout,
        }
        
        # 配置文件放在 exe 同目录
        exe_dir = os.path.dirname(self.exe_path)
        self._config_path = os.path.join(exe_dir or ".", self.config_filename)
        
        with open(self._config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"[Launcher] Config written to {self._config_path}")
    
    def _remove_config(self):
        """删除配置文件"""
        if self._config_path and os.path.exists(self._config_path):
            os.remove(self._config_path)
            print(f"[Launcher] Config file removed")
    
    def _wait_for_ready(self, start_time: float):
        """等待游戏 Socket 就绪"""
        print(f"[Launcher] Waiting for game to start on port {self.port}...")
        
        while time.perf_counter() - start_time < self.startup_timeout:
            # 检查进程是否还活着
            if self._process and self._process.process.poll() is not None:
                raise RuntimeError("Game process exited unexpectedly")
            
            # 尝试连接
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                sock.connect((self.host, self.port))
                sock.close()
                print(f"[Launcher] Game ready! ({time.perf_counter() - start_time:.2f}s)")
                return
            except (socket.error, ConnectionRefusedError):
                time.sleep(0.2)
        
        raise TimeoutError(
            f"Game did not start within {self.startup_timeout}s. "
            f"Check if the game supports --test-mode or test_mode.json"
        )
    
    def stop(self):
        """停止游戏"""
        if self._process is None:
            return
        
        print("[Launcher] Stopping game...")
        
        # 1. 尝试优雅关闭
        self._process.process.terminate()
        
        try:
            self._process.process.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            # 2. 强制关闭
            print("[Launcher] Force killing game...")
            self._process.process.kill()
            self._process.process.wait()
        
        # 3. 删除配置文件
        self._remove_config()
        
        self._process = None
        print("[Launcher] Game stopped")
    
    def is_running(self) -> bool:
        """检查游戏是否运行"""
        if self._process is None:
            return False
        return self._process.process.poll() is None
    
    def get_output(self) -> tuple:
        """获取游戏输出"""
        if self._process is None:
            return "", ""
        
        stdout = ""
        stderr = ""
        
        if self._process.process.stdout:
            try:
                stdout = self._process.process.stdout.read().decode('utf-8', errors='ignore')
            except:
                pass
        
        if self._process.process.stderr:
            try:
                stderr = self._process.process.stderr.read().decode('utf-8', errors='ignore')
            except:
                pass
        
        return stdout, stderr
    
    def kill_orphan_processes(self, process_name: str = None):
        """清理孤儿进程"""
        if process_name is None:
            # 从 exe 路径提取进程名
            process_name = os.path.basename(self.exe_path).replace('.exe', '')
        
        killed = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    proc.kill()
                    killed.append(proc.info['pid'])
            except:
                pass
        
        if killed:
            print(f"[Launcher] Killed orphan processes: {killed}")
        
        return killed
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False
