"""
游戏端测试配置读取器
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
        """从配置文件读取
        
        配置文件格式:
        {
            "enabled": true,
            "port": 9876,
            "host": "localhost"
        }
        """
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
        """从环境变量读取
        
        环境变量:
        - GAME_TEST_MODE=1
        - GAME_TEST_PORT=9876
        - GAME_TEST_HOST=localhost
        """
        enabled = os.environ.get("GAME_TEST_MODE", "0") == "1"
        port = int(os.environ.get("GAME_TEST_PORT", "9876"))
        host = os.environ.get("GAME_TEST_HOST", "localhost")
        
        return cls(enabled=enabled, port=port, host=host)
    
    def __str__(self):
        return f"TestModeConfig(enabled={self.enabled}, port={self.port}, host='{self.host}')"
