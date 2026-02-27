# OpenCode Demo 文档索引

本仓库包含 OpenCode 各功能的最小可行性 demo 和详细文档。

## 功能列表

| 功能 | 目录 | 文档 |
|------|------|------|
| 插件 (Plugins) | `plugins/` | [plugins.md](./plugins.md) |
| MCP 服务 | `mcp-servers/` | [mcp-servers.md](./mcp-servers.md) |
| 代理 (Agents) | `agents/` | [agents.md](./agents.md) |
| 技能 (Skills) | `skills/` | [skills.md](./skills.md) |
| 命令 (Commands) | `commands/` | [commands.md](./commands.md) |
| 规则 (Rules) | `AGENTS.md` | [rules.md](./rules.md) |
| 配置 (Config) | `opencode.example.json` | [config.md](./config.md) |

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/kongshan001/opencode-demo.git
cd opencode-demo
```

### 2. 安装 MCP 服务依赖

```bash
cd mcp-servers/calculator && bun install
cd ../echo && bun install
```

### 3. 配置 OpenCode

复制示例配置到你的项目：

```bash
cp opencode.example.json /path/to/your/project/opencode.json
```

### 4. 使用插件

将需要的插件复制到 OpenCode 插件目录：

```bash
# 项目级
cp plugins/*.ts /path/to/your/project/.opencode/plugins/

# 或全局
cp plugins/*.ts ~/.config/opencode/plugins/
```

## 功能概览

### 插件 (Plugins)

TypeScript 编写的扩展，可以：
- 拦截和修改工具调用
- 注入环境变量
- 添加自定义工具
- 监听事件

### MCP 服务

Model Context Protocol 服务器，可以：
- 提供外部工具给 LLM
- 连接外部数据源
- 实现自定义功能

### 代理 (Agents)

专门的 AI 助手，可以：
- 处理特定类型的任务
- 使用不同的模型配置
- 拥有不同的权限级别

### 技能 (Skills)

可复用的行为定义，可以：
- 封装最佳实践
- 提供上下文指导
- 按需加载

### 命令 (Commands)

自定义斜杠命令，可以：
- 快速执行常用任务
- 接收参数
- 集成 Shell 命令

## 目录结构

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
│   └── echo/                  # Echo 服务
├── agents/                    # 自定义代理
│   ├── code-reviewer.md       # 代码审查
│   └── test-engineer.md       # 测试工程师
├── skills/                    # 技能定义
│   ├── code-review/           # 代码审查技能
│   └── git-workflow/          # Git 工作流
├── commands/                  # 自定义命令
│   ├── analyze.md             # 项目分析
│   ├── component.md           # 创建组件
│   └── test.md                # 运行测试
├── docs/                      # 文档
│   ├── plugins.md
│   ├── mcp-servers.md
│   ├── agents.md
│   ├── skills.md
│   ├── commands.md
│   ├── rules.md
│   └── config.md
├── AGENTS.md                  # 项目规则
├── opencode.example.json      # 配置示例
└── README.md
```
