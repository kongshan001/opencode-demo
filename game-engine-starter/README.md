# Python 游戏引擎开发环境

这是一个为 **Python + 自研游戏引擎** 开发准备的 OpenCode 配置环境。

## 📁 目录结构

```
.opencode/
├── agents/                     # 自定义代理
│   ├── python-reviewer.md     # Python 代码审查
│   ├── performance-analyst.md # 性能分析
│   └── game-tester.md         # 游戏测试
├── skills/                     # 技能定义
│   ├── python-dev/            # Python 开发
│   │   └── SKILL.md
│   ├── game-engine/           # 游戏引擎
│   │   └── SKILL.md
│   └── performance-opt/       # 性能优化
│       └── SKILL.md
├── commands/                   # 自定义命令
│   ├── run.md                 # 运行游戏
│   ├── test.md                # 运行测试
│   ├── lint.md                # 代码检查
│   ├── profile.md             # 性能分析
│   ├── entity.md              # 创建实体
│   └── system.md              # 创建系统
├── plugins/                    # 插件
│   ├── python-game.ts         # Python 游戏工具
│   ├── performance-monitor.ts # 性能监控
│   └── python-guard.ts        # 代码保护
├── AGENTS.md                   # 项目规则
└── README.md                   # 本文件
```

## 🚀 使用方法

### 方法 1: 复制到项目目录

```bash
# 复制整个 .opencode 目录到你的项目根目录
cp -r .opencode /path/to/your/game-project/

# 复制配置文件
cp opencode.json /path/to/your/game-project/
```

### 方法 2: 复制到全局目录

```bash
# 复制到全局配置目录（所有项目可用）
cp -r .opencode ~/.config/opencode/
```

## 📦 包含内容

### 代理 (3个)

| 代理 | 功能 | 调用方式 |
|------|------|----------|
| `python-reviewer` | Python 代码审查 | `@python-reviewer` |
| `performance-analyst` | 性能分析 | `@performance-analyst` |
| `game-tester` | 测试编写 | `@game-tester` |

### 技能 (3个)

| 技能 | 功能 |
|------|------|
| `python-dev` | Python 开发最佳实践 |
| `game-engine` | 游戏引擎设计模式 |
| `performance-opt` | 性能优化技巧 |

### 命令 (6个)

| 命令 | 功能 |
|------|------|
| `/run` | 运行游戏 |
| `/test` | 运行测试 |
| `/lint` | 代码质量检查 |
| `/profile` | 性能分析 |
| `/entity <name>` | 创建实体类 |
| `/system <name>` | 创建系统类 |

### 插件 (3个)

| 插件 | 功能 |
|------|------|
| `python-game.ts` | 自定义工具（生成模板、测试等） |
| `performance-monitor.ts` | 性能监控 |
| `python-guard.ts` | 代码安全保护 |

## 📝 AGENTS.md 说明

项目规则文件包含：

- 技术栈说明
- 项目结构指南
- 代码规范
- 命名约定
- 游戏开发规范
- 性能优化建议
- 开发工作流

## ⚙️ 配置说明

### opencode.json

主配置文件包含：

- 模型设置
- 代理配置
- 命令定义
- 权限设置
- 文件监视忽略规则

### 权限配置

```json
{
  "permission": {
    "edit": "ask",           // 编辑文件需确认
    "bash": {
      "git push": "ask",     // git push 需确认
      "pip install *": "ask" // 安装包需确认
    }
  }
}
```

## 🔧 自定义

### 添加新代理

```bash
# 创建代理文件
touch .opencode/agents/my-agent.md
```

### 添加新命令

```bash
# 创建命令文件
touch .opencode/commands/my-command.md
```

### 添加新技能

```bash
# 创建技能目录和文件
mkdir .opencode/skills/my-skill
touch .opencode/skills/my-skill/SKILL.md
```

## 📋 推荐项目结构

```
your-game-project/
├── .opencode/          # 本配置
├── opencode.json       # 主配置
├── src/
│   ├── engine/         # 引擎核心
│   ├── game/           # 游戏逻辑
│   └── utils/          # 工具函数
├── tests/              # 测试
├── assets/             # 资源
├── main.py             # 入口
└── pyproject.toml      # Python 配置
```

## 🛠 依赖工具

推荐安装：

```bash
# 代码格式化
pip install black isort

# 类型检查
pip install mypy

# 代码检查
pip install pylint

# 测试
pip install pytest pytest-cov
```

## 📚 文档参考

- [Python 开发技能](.opencode/skills/python-dev/SKILL.md)
- [游戏引擎技能](.opencode/skills/game-engine/SKILL.md)
- [性能优化技能](.opencode/skills/performance-opt/SKILL.md)
- [项目规则](.opencode/AGENTS.md)
