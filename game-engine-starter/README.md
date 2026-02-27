# Python 游戏引擎开发环境

这是一个为 **Python + 自研游戏引擎** 开发准备的 OpenCode 配置环境。

## 🚀 快速开始

### 下载并移植

```bash
# 克隆仓库
git clone https://github.com/kongshan001/opencode-demo.git

# 复制到你的游戏项目
cp -r opencode-demo/game-engine-starter/.opencode /path/to/your/game-project/
cp opencode-demo/game-engine-starter/opencode.json /path/to/your/game-project/
cp opencode-demo/game-engine-starter/pyproject.toml /path/to/your/game-project/
```

## 📁 目录结构

```
.opencode/
├── agents/                     # 自定义代理
│   ├── python-reviewer.md     # Python 代码审查
│   ├── performance-analyst.md # 性能分析
│   ├── game-tester.md         # 游戏测试
│   └── engine-tester.md       # 引擎测试（Mock 架构）
├── skills/                     # 技能定义
│   ├── python-dev/            # Python 开发
│   ├── game-engine/           # 游戏引擎模式
│   ├── performance-opt/       # 性能优化
│   └── engine-testing/        # 引擎测试策略 ⭐
├── commands/                   # 自定义命令
│   ├── run.md                 # 运行游戏
│   ├── test.md                # 运行测试
│   ├── lint.md                # 代码检查
│   ├── profile.md             # 性能分析
│   ├── benchmark.md           # 基准测试 ⭐
│   ├── stress.md              # 压力测试 ⭐
│   ├── coverage.md            # 覆盖率 ⭐
│   ├── entity.md              # 创建实体
│   └── system.md              # 创建系统
├── plugins/                    # 插件
│   ├── python-game.ts         # Python 游戏工具
│   ├── performance-monitor.ts # 性能监控
│   └── python-guard.ts        # 代码保护
├── AGENTS.md                   # 项目规则
└── README.md
```

## ⭐ 自动化测试策略

### 核心思路：分层 Mock

```
┌─────────────────────────────────────────────────┐
│                 测试金字塔                        │
├─────────────────────────────────────────────────┤
│  E2E 测试 (少量)    - 完整游戏流程（需渲染）       │
│  ─────────────────────────────────────────────  │
│  集成测试 (中等)    - 系统交互（Mock 渲染）       │
│  ─────────────────────────────────────────────  │
│  单元测试 (大量)    - 核心算法（无依赖）          │
└─────────────────────────────────────────────────┘
```

### Mock 架构

```python
# tests/conftest.py

class MockRenderer:
    """模拟渲染器 - 不实际绘制"""
    def __init__(self):
        self.draw_calls = []
    
    def draw(self, sprite):
        self.draw_calls.append(sprite)  # 只记录
    
    @property
    def draw_count(self):
        return len(self.draw_calls)

class TestEngineContext:
    """测试用引擎上下文"""
    def __init__(self):
        self.renderer = MockRenderer()
        self.window = MockWindow()
        self.audio = MockAudio()
    
    def create_entity(self, *components):
        # 创建测试实体
        pass
```

### 测试示例

```python
# 单元测试 - 纯逻辑，无依赖
def test_vector_addition():
    v1 = Vector2(1, 2)
    v2 = Vector2(3, 4)
    assert (v1 + v2) == Vector2(4, 6)

# 集成测试 - 使用 Mock
def test_entity_movement(engine):
    entity = engine.create_entity(
        Transform(x=0, y=0),
        Velocity(dx=10, dy=5)
    )
    
    engine.update(1.0)
    
    transform = entity.get_component(Transform)
    assert transform.x == 10

# 渲染测试 - Mock 渲染器
def test_rendering(engine):
    for _ in range(100):
        engine.create_entity()
    
    engine.render()
    
    assert engine.renderer.draw_count == 100
```

## ⭐ 性能压测方案

### 基准测试

```python
# tests/benchmark/test_core_performance.py

def test_entity_creation_1000(benchmark):
    def create_1000():
        return [Entity() for _ in range(1000)]
    
    result = benchmark(create_1000)
    assert result.mean_time < 0.1  # 100ms 内
```

### 压力测试

```python
# tests/stress/test_load.py

def test_10000_entities_sustained():
    entities = [Entity() for _ in range(10000)]
    
    for _ in range(3600):  # 60 秒 @ 60 FPS
        system.update(entities, 0.016)
```

### 性能基线

| 测试项 | 基线 | 说明 |
|--------|------|------|
| 实体创建 (1000个) | < 100ms | 基础性能 |
| 实体更新 (1000个) | < 1ms | 每帧开销 |
| 向量运算 | < 0.01ms | 数学核心 |
| 碰撞检测 | < 0.5ms | 物理系统 |

## 📦 包含内容

### 代理 (4个)

| 代理 | 功能 | 调用方式 |
|------|------|----------|
| `@python-reviewer` | Python 代码审查 | `@python-reviewer` |
| `@performance-analyst` | 性能分析 | `@performance-analyst` |
| `@game-tester` | 游戏测试 | `@game-tester` |
| `@engine-tester` | 引擎测试、Mock 架构 | `@engine-tester` |

### 技能 (4个)

| 技能 | 内容 |
|------|------|
| `python-dev` | Python 代码规范、类型注解 |
| `game-engine` | ECS 架构、游戏循环、对象池 |
| `performance-opt` | 性能优化技巧 |
| `engine-testing` | **自动化测试策略、Mock 架构、性能压测** |

### 命令 (9个)

| 命令 | 功能 |
|------|------|
| `/run` | 运行游戏 |
| `/test` | 运行测试套件 |
| `/lint` | 代码质量检查 |
| `/profile` | 性能分析 |
| `/benchmark` | **运行基准测试** |
| `/stress` | **运行压力测试** |
| `/coverage` | **生成覆盖率报告** |
| `/entity <name>` | 创建实体类 |
| `/system <name>` | 创建系统类 |

### 插件 (3个)

| 插件 | 功能 |
|------|------|
| `python-game.ts` | 自定义工具 |
| `performance-monitor.ts` | 性能监控 |
| `python-guard.ts` | 代码安全 |

## 📋 推荐项目结构

```
your-game-project/
├── .opencode/          # 本配置
├── opencode.json       # 主配置
├── pyproject.toml      # Python 配置
├── src/
│   ├── engine/         # 引擎核心
│   ├── game/           # 游戏逻辑
│   └── utils/          # 工具函数
├── tests/              # 测试
│   ├── conftest.py     # Mock 定义
│   ├── unit/           # 单元测试
│   ├── integration/    # 集成测试
│   ├── benchmark/      # 基准测试
│   └── stress/         # 压力测试
├── main.py             # 入口
└── README.md
```

## 🛠 安装依赖

```bash
# 测试框架
pip install pytest pytest-cov pytest-benchmark pytest-xdist

# 代码质量
pip install black isort mypy pylint

# 可选：性能分析
pip install py-spy memory_profiler
```

## 📚 详细文档

- [AGENTS.md](.opencode/AGENTS.md) - 项目规则
- [engine-testing/SKILL.md](.opencode/skills/engine-testing/SKILL.md) - **完整测试策略**
- [tests/README.md](tests/README.md) - 测试目录说明

## 🔄 CI/CD 集成

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: pytest tests/unit tests/integration -v

- name: Run benchmarks
  run: pytest tests/benchmark --benchmark-only

- name: Check coverage
  run: pytest --cov=src --cov-fail-under=80
```
