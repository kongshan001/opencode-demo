/**
 * Echo MCP Server
 * 
 * 一个最简单的 MCP 服务，用于演示 MCP 协议的基本结构。
 * 提供一个 echo 工具，将输入原样返回。
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js"
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js"
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError,
} from "@modelcontextprotocol/sdk/types.js"

const server = new Server(
  { name: "echo", version: "1.0.0" },
  { capabilities: { tools: {} } }
)

// 列出可用工具
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "echo",
      description: "将输入文本原样返回，用于测试 MCP 连接",
      inputSchema: {
        type: "object",
        properties: {
          message: {
            type: "string",
            description: "要回显的消息",
          },
        },
        required: ["message"],
      },
    },
    {
      name: "reverse",
      description: "反转输入文本",
      inputSchema: {
        type: "object",
        properties: {
          text: {
            type: "string",
            description: "要反转的文本",
          },
        },
        required: ["text"],
      },
    },
  ],
}))

// 处理工具调用
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params

  switch (name) {
    case "echo":
      return {
        content: [{ type: "text", text: `Echo: ${args?.message}` }],
      }
    case "reverse":
      const reversed = (args?.text as string).split("").reverse().join("")
      return {
        content: [{ type: "text", text: `Reversed: ${reversed}` }],
      }
    default:
      throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`)
  }
})

// 启动服务
async function main() {
  const transport = new StdioServerTransport()
  await server.connect(transport)
  console.error("Echo MCP Server started")
}

main().catch(console.error)
