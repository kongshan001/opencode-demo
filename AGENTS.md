# OpenCode Demo 项目

这是一个演示 OpenCode 各功能的最小可行性示例项目。

## 项目结构

```
opencode-demo/
├── plugins/           # TypeScript 插件示例
├── mcp-servers/       # MCP 服务示例
├── agents/            # 自定义代理定义
├── skills/            # 技能定义
├── commands/          # 自定义命令
└── docs/              # 详细文档
```

## 技术栈

- OpenCode (AI 编码代理)
- TypeScript / Bun
- MCP (Model Context Protocol)

## 使用指南

### 插件使用

1. 将 `plugins/*.ts` 复制到 `.opencode/plugins/` 或 `~/.config/opencode/plugins/`
2. 重启 OpenCode

### MCP 服务使用

1. 安装依赖：
   ```bash
   cd mcp-servers/calculator && bun install
   cd ../echo && bun install
   ```

2. 在 `opencode.json` 中配置：
   ```json
   {
     "mcp": {
       "calculator": {
         "type": "local",
         "command": ["bun", "run", "/path/to/opencode-demo/mcp-servers/calculator/index.ts"],
         "enabled": true
       }
     }
   }
   ```

### 代理使用

- 将 `agents/*.md` 复制到 `.opencode/agents/`
- 使用 `@agent-name` 调用

### 技能使用

- 将 `skills/*/` 复制到 `.opencode/skills/`
- 模型会自动发现并按需加载

### 命令使用

- 将 `commands/*.md` 复制到 `.opencode/commands/`
- 使用 `/command-name` 执行

## 文档

详细文档位于 `docs/` 目录：

- [plugins.md](docs/plugins.md) - 插件开发指南
- [mcp-servers.md](docs/mcp-servers.md) - MCP 服务开发指南
- [agents.md](docs/agents.md) - 代理配置指南
- [skills.md](docs/skills.md) - 技能定义指南
- [commands.md](docs/commands.md) - 命令创建指南
- [rules.md](docs/rules.md) - 规则配置指南
- [config.md](docs/config.md) - 配置参考

## 开发规范

### 插件开发

- 使用 TypeScript
- 遵循 Plugin 接口
- 添加 JSDoc 注释

### MCP 服务开发

- 使用 @modelcontextprotocol/sdk
- 实现工具、资源、提示
- 处理错误情况

### 文档编写

- 使用 Markdown
- 包含代码示例
- 说明卡点和解决方案
