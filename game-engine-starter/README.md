# Python 游戏引擎开发环境
这是一个为 **Python + 自研游戏引擎** 开发准备的 OpenCode 配置环境。

## 🚀 快速开始
### 下载并移植
```bash
git clone https://github.com/kongshan001/opencode-demo.git
cd opencode-demo/game-engine-starter
cp -r .opencode /path/to/your/game-project/
cp game-engine-starter/opencode.json /path/to/your/game-project/
```

---

## 📁 目录结构

```
game-engine-starter/
├── .opencode/           # 开放代码配置
│   ├── agents/              # 自定义代理
│   │   ├── python-reviewer.md     # Python 代码审查
│   │   ├── performance-analyst.md # 性能分析
│   │   ├── game-tester.md         # 游戏测试
│   │   ├── engine-tester.md       # 引擎测试（Mock 架构）
│   │   └── e2e-tester.md        # E2E 测试（Socket)
│   ├── commands/            # 自定义命令
│   │   ├── run.md               # 运行游戏
│   │   ├── test.md               # 运行测试
│   │   ├── lint.md               # 代码检查
│   │   ├── profile.md             # 性能分析
│   │   ├── benchmark.md           # 基准测试
│   │   ├── stress.md              # 压力测试
│   │   ├── coverage.md             # 覆盖率报告
│   │   ├── e2e.md                # E2E 测试
│   │   ├── generate-socket-test.md # 生成 Socket 测试代码
│   │   └── generate-entity.md       # 生成实体类
│   ├── skills/               # 技能定义
│   │   ├── python-dev/           # Python 开发规范
│   │   ├── game-engine/           # 游戏引擎模式
│   │   ├── performance-opt/       # 性能优化技巧
│   │   ├── engine-testing/       # 自动化测试策略
│   │   └── socket-testing/       # **Socket 通信测试** ⭐
│   ├── plugins/              # 插件
│   │   ├── python-game.ts         # Python 游戏工具
│   │   ├── performance-monitor.ts # 性能监控
│   │   └── python-guard.ts         # 代码保护
│   ├── AGENTS.md                  # 项目规则
│   ├── opencode.json               # 主配置
│   ├── pyproject.toml               # pytest 配置
│   └── README.md                 # 本文件
```

---

## ⭐ 新增：Socket 通信自动化测试

```
┌─────────────────────────────────────────────────────┐
│                    E2E 测试架构                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│  │  测试框架    │ ◄──────────────────────►│   游戏进程   │
│  │  (pytest)    │    JSON 指令/响应       │  Socket 服务   │
│  │              │                         │              │
└──────────────┘                         └──────────────┘
```
---

## 🔧 安装依赖

```bash
pip install pytest pytest-cov pytest-benchmark
```

### 2. 游戏端集成

在游戏入口添加测试模式支持：

```python
# main.py
from engine.game import Game
from engine.testing.socket_server import GameTestServer
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

---

### 3. 运行测试

```bash
# 运行所有 E2E 测试
pytest tests/e2e -v

```

---

### 4. E2E 测试示例

```python
# tests/e2e/test_game_basic.py
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

---

### 5. CI/CD 集成

```yaml
# .github/workflows/e2e.yml
- name: Run E2E tests
  run: |
    python tests/e2e/runner.py main.py
  ```
`

---

## 📚 详细文档

- **技能文档**: `.opencode/skills/socket-testing/SKILL.md` (32KB)
- **测试框架**: `.opencode/src/engine/testing/` (完整实现)
- **代理文档**: `.opencode/agents/`
- **命令文档**: `.opencode/commands/`
- **README**: `game-engine-starter/README.md`

---

## 🎯 总结

已创建完整的 Socket 通信自动化测试方案，包括：

### 架构
```
┌─────────────────────────────────────────────────────┐
│                    E2E 测试架构                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│  │  测试框架    │ ◄──────────────────────►│   游戏进程   │
│  │  (pytest)    │    JSON 指令/响应       │  Socket 服务   │
│  │              │                         │              │
└──────────────┘                         └──────────────┘
```
```

### 游戏端修改
1. 在游戏入口 `main.py` 添加测试模式参数
2. 在游戏启动时创建 `GameTestServer`

### 运行测试
```bash
pytest tests/e2e -v
```

---

### 示例测试用例

```python
# tests/e2e/test_game_logic.py
import pytest
from tests.e2e.conftest import game_client, paused_game


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
```
```

---

### 🔧 自定义指令
你可以通过 `register_handler` 注册自定义指令：

### 示例：注册场景切换指令

```python
# 在游戏初始化时注册
def register_scene_change_handler(command_type: str, handler: Callable):
    """注册场景切换指令处理器"""
    pass

```

---

## 🎯 宦装测试命令

| 匇令类型 | 功能 |
|--------|------|
| `/run` | 运行游戏 |
| `/test` | 运行测试 |
| `/lint` | 代码检查 |
| `/profile` | 性能分析 |
| `/benchmark` | 基准测试 |
| `/stress` | 压力测试 |
| `/coverage` | 覆盖率报告 |
| `/e2e` | E2E 测试 |
| `/generate-socket-test` | 生成测试代码 |
| `/generate-entity` | 生成实体类 |

---

## 📦 完整文档

- **AGENTS.md** - 项目规则
- **socket-testing/SKILL.md** - Socket 测试完整实现
- **tests/README.md** - 测试目录说明
- **pyproject.toml** - pytest 配置

- **opencode.json** - 主配置
- **README.md** - 使用说明

