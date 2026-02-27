# OpenCode MCP 服务开发指南

## 概述

MCP (Model Context Protocol) 是一种标准协议，用于为 LLM 提供外部工具和数据。

## 接入方式

### 1. 本地 MCP 服务

在 `opencode.json` 中配置：

```json
{
  "mcp": {
    "my-local-server": {
      "type": "local",
      "command": ["bun", "run", "./path/to/server.ts"],
      "enabled": true,
      "environment": {
        "MY_ENV": "value"
      }
    }
  }
}
```

### 2. 远程 MCP 服务

```json
{
  "mcp": {
    "my-remote-server": {
      "type": "remote",
      "url": "https://api.example.com/mcp",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer {env:API_KEY}"
      }
    }
  }
}
```

### 3. npm 包

```json
{
  "mcp": {
    "npm-server": {
      "type": "local",
      "command": ["npx", "-y", "@org/mcp-server"]
    }
  }
}
```

## 功能

### 工具 (Tools)

提供可调用的函数：

```typescript
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: "my_tool",
    description: "工具描述",
    inputSchema: {
      type: "object",
      properties: {
        param: { type: "string", description: "参数说明" }
      },
      required: ["param"]
    }
  }]
}))

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params
  
  if (name === "my_tool") {
    // 处理逻辑
    return {
      content: [{ type: "text", text: "结果" }]
    }
  }
})
```

### 资源 (Resources)

提供可读取的数据：

```typescript
server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: [{
    uri: "file:///path/to/resource",
    name: "资源名称",
    mimeType: "text/plain"
  }]
}))
```

### 提示 (Prompts)

提供预定义的提示模板：

```typescript
server.setRequestHandler(ListPromptsRequestSchema, async () => ({
  prompts: [{
    name: "my_prompt",
    description: "提示描述",
    arguments: [{
      name: "arg1",
      description: "参数说明",
      required: true
    }]
  }]
}))
```

## 推进过程

### 步骤 1: 创建项目

```bash
mkdir my-mcp-server
cd my-mcp-server
bun init
bun add @modelcontextprotocol/sdk
```

### 步骤 2: 创建服务

```typescript
// index.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js"
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js"
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js"

const server = new Server(
  { name: "my-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
)

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [/* 工具定义 */]
}))

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  // 处理调用
})

async function main() {
  const transport = new StdioServerTransport()
  await server.connect(transport)
}

main().catch(console.error)
```

### 步骤 3: 测试服务

```bash
bun run index.ts
```

### 步骤 4: 配置 OpenCode

在 `opencode.json` 中添加配置。

## 卡点与解决方案

### 1. 通信协议错误

**问题**: 服务启动但 OpenCode 无法连接

**解决**: 
- 确保使用 `StdioServerTransport`
- 检查命令路径是否正确
- 查看服务启动日志

### 2. 工具不显示

**问题**: 工具没有出现在 OpenCode 中

**解决**:
- 检查 `enabled: true`
- 验证 `inputSchema` 格式正确
- 确认服务没有崩溃

### 3. 超时问题

**问题**: 工具调用超时

**解决**:
```json
{
  "mcp": {
    "my-server": {
      "timeout": 10000  // 10秒
    }
  }
}
```

### 4. 环境变量问题

**问题**: 服务需要环境变量

**解决**:
```json
{
  "mcp": {
    "my-server": {
      "environment": {
        "API_KEY": "{env:MY_API_KEY}"
      }
    }
  }
}
```

## 示例服务

### 最小 Echo 服务

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js"
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js"
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js"

const server = new Server(
  { name: "echo", version: "1.0.0" },
  { capabilities: { tools: {} } }
)

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: "echo",
    description: "回显消息",
    inputSchema: {
      type: "object",
      properties: {
        message: { type: "string" }
      },
      required: ["message"]
    }
  }]
}))

server.setRequestHandler(CallToolRequestSchema, async (request) => ({
  content: [{ type: "text", text: `Echo: ${request.params.arguments?.message}` }]
}))

const transport = new StdioServerTransport()
server.connect(transport)
```

## 最佳实践

1. **错误处理**: 使用 `McpError` 返回标准错误
2. **日志**: 使用 `console.error()` 输出调试信息
3. **类型安全**: 使用 TypeScript 定义类型
4. **文档**: 为每个工具添加清晰的描述
5. **验证**: 验证输入参数
