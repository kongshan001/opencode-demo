# OpenCode Demo

OpenCode 各功能的最小可行性 demo 和详细文档。

## 📦 包含内容

### 插件 (Plugins)

| 文件 | 功能 |
|------|------|
| `plugins/custom-tool.ts` | 添加自定义工具（时间戳、JSON格式化、Base64） |
| `plugins/env-injection.ts` | 注入环境变量到 Shell 命令 |
| `plugins/notification.ts` | 会话完成时发送通知 |
| `plugins/session-logger.ts` | 记录会话事件日志 |
| `plugins/tool-guard.ts` | 工具执行守卫，阻止危险操作 |

### MCP 服务

| 服务 | 功能 |
|------|------|
| `mcp-servers/calculator/` | 计算器服务（加法、乘法） |
| `mcp-servers/echo/` | Echo 服务（回显、反转文本） |

### 代理 (Agents)

| 代理 | 功能 |
|------|------|
| `agents/code-reviewer.md` | 代码审查专家 |
| `agents/test-engineer.md` | 测试工程师 |

### 技能 (Skills)

| 技能 | 功能 |
|------|------|
| `skills/code-review/` | 代码审查流程 |
| `skills/git-workflow/` | Git 工作流指南 |

### 命令 (Commands)

| 命令 | 功能 |
|------|------|
| `/test` | 运行测试套件 |
| `/analyze` | 分析项目结构 |
| `/component <name>` | 创建新组件 |

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/kongshan001/opencode-demo.git
cd opencode-demo
```

### 2. 安装 MCP 服务依赖

```bash
cd mcp-servers/calculator && bun install
cd ../echo && bun install
cd ../..
```

### 3. 复制配置示例

```bash
cp opencode.example.json /path/to/your/project/opencode.json
```

### 4. 使用插件

```bash
# 项目级
cp plugins/*.ts /path/to/your/project/.opencode/plugins/

# 或全局
cp plugins/*.ts ~/.config/opencode/plugins/
```

## 📚 文档

| 文档 | 内容 |
|------|------|
| [docs/plugins.md](docs/plugins.md) | 插件开发：接入、功能、卡点 |
| [docs/mcp-servers.md](docs/mcp-servers.md) | MCP 服务：协议、开发、调试 |
| [docs/agents.md](docs/agents.md) | 代理配置：类型、权限、示例 |
| [docs/skills.md](docs/skills.md) | 技能定义：结构、发现、权限 |
| [docs/commands.md](docs/commands.md) | 命令创建：参数、Shell、代理 |
| [docs/rules.md](docs/rules.md) | 规则配置：AGENTS.md 编写 |
| [docs/config.md](docs/config.md) | 配置参考：完整选项说明 |

## 📁 目录结构

```
opencode-demo/
├── plugins/                    # 插件示例
│   ├── custom-tool.ts         # 自定义工具
│   ├── env-injection.ts       # 环境变量注入
│   ├── notification.ts        # 通知插件
│   ├── session-logger.ts      # 会话日志
│   └── tool-guard.ts          # 工具守卫
├── mcp-servers/               # MCP 服务示例
│   ├── calculator/            # 计算器服务
│   │   ├── index.ts
│   │   └── package.json
│   └── echo/                  # Echo 服务
│       ├── index.ts
│       └── package.json
├── agents/                    # 自定义代理
│   ├── code-reviewer.md       # 代码审查
│   └── test-engineer.md       # 测试工程师
├── skills/                    # 技能定义
│   ├── code-review/           # 代码审查技能
│   │   └── SKILL.md
│   └── git-workflow/          # Git 工作流
│       └── SKILL.md
├── commands/                  # 自定义命令
│   ├── analyze.md             # 项目分析
│   ├── component.md           # 创建组件
│   └── test.md                # 运行测试
├── docs/                      # 详细文档
│   ├── README.md              # 文档索引
│   ├── plugins.md
│   ├── mcp-servers.md
│   ├── agents.md
│   ├── skills.md
│   ├── commands.md
│   ├── rules.md
│   └── config.md
├── AGENTS.md                  # 项目规则
├── opencode.example.json      # 配置示例
└── README.md                  # 本文件
```

## 🔧 配置示例

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-20250514",
  
  "mcp": {
    "calculator": {
      "type": "local",
      "command": ["bun", "run", "./mcp-servers/calculator/index.ts"],
      "enabled": true
    },
    "echo": {
      "type": "local",
      "command": ["bun", "run", "./mcp-servers/echo/index.ts"],
      "enabled": true
    }
  },
  
  "plugin": [],
  
  "permission": {
    "edit": "ask",
    "bash": {
      "git push": "ask"
    }
  }
}
```

## 📝 每个功能的接入流程

### 插件
1. 创建 `.opencode/plugins/` 目录
2. 复制 `.ts` 文件到该目录
3. 重启 OpenCode

### MCP 服务
1. 安装依赖 `bun install`
2. 在 `opencode.json` 中配置
3. 设置 `enabled: true`

### 代理
1. 复制 `.md` 文件到 `.opencode/agents/`
2. 使用 `@agent-name` 调用

### 技能
1. 复制 `skills/*/` 到 `.opencode/skills/`
2. 模型自动发现

### 命令
1. 复制 `.md` 文件到 `.opencode/commands/`
2. 使用 `/command-name` 执行

## 📄 许可证

MIT
