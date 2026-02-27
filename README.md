# OpenCode Demo

一个演示 OpenCode 插件和 MCP 服务的示例仓库。

## 项目结构

```
opencode-demo/
├── plugins/
│   └── session-logger.ts    # 会话日志记录插件
├── mcp-servers/
│   └── calculator/          # 计算器 MCP 服务
│       ├── index.ts
│       └── package.json
└── README.md
```

## 插件：Session Logger

一个简单的 OpenCode 插件，用于记录会话事件。

### 功能

- 会话完成时记录日志
- 文件编辑时记录日志

### 使用方法

将 `plugins/session-logger.ts` 复制到 OpenCode 插件目录：

```bash
# 项目级插件
cp plugins/session-logger.ts .opencode/plugins/

# 或全局插件
cp plugins/session-logger.ts ~/.config/opencode/plugins/
```

## MCP 服务：Calculator

一个简单的本地 MCP 服务，提供基础计算工具。

### 工具

- `add`: 将两个数字相加
- `multiply`: 将两个数字相乘

### 配置

在 OpenCode 配置文件中添加：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "calculator": {
      "type": "local",
      "command": ["bun", "run", "/path/to/opencode-demo/mcp-servers/calculator/index.ts"],
      "enabled": true
    }
  }
}
```

### 使用

在提示词中添加 `use calculator` 即可使用计算器工具：

```
计算 123 加 456，use calculator
```

## 开发环境

- Bun runtime
- TypeScript

## 许可证

MIT
