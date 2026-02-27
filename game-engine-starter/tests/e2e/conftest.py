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

# exe 文件路径 - 改成你的 exe 路径
EXE_PATH = r"D:\mygame\mygame.exe"

# 或者从环境变量读取
# EXE_PATH = os.environ.get("GAME_EXE_PATH", r"D:\mygame\mygame.exe")

# Socket 端口
PORT = 9876

# 启动超时（秒）
STARTUP_TIMEOUT = 30.0


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(scope="session")
def game_launcher():
    """游戏启动器（session 级别）"""
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
