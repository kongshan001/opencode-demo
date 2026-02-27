/**
 * Calculator MCP Server
 * 
 * 一个简单的本地 MCP 服务，提供基础计算工具。
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js"
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js"
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError,
} from "@modelcontextprotocol/sdk/types.js"

// 创建 MCP 服务器
const server = new Server(
  {
    name: "calculator",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
)

// 定义工具列表
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "add",
        description: "将两个数字相加",
        inputSchema: {
          type: "object",
          properties: {
            a: {
              type: "number",
              description: "第一个数字",
            },
            b: {
              type: "number",
              description: "第二个数字",
            },
          },
          required: ["a", "b"],
        },
      },
      {
        name: "multiply",
        description: "将两个数字相乘",
        inputSchema: {
          type: "object",
          properties: {
            a: {
              type: "number",
              description: "第一个数字",
            },
            b: {
              type: "number",
              description: "第二个数字",
            },
          },
          required: ["a", "b"],
        },
      },
    ],
  }
})

// 处理工具调用
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params

  switch (name) {
    case "add": {
      const a = args?.a as number
      const b = args?.b as number
      if (typeof a !== "number" || typeof b !== "number") {
        throw new McpError(ErrorCode.InvalidParams, "参数必须是数字")
      }
      const result = a + b
      return {
        content: [
          {
            type: "text",
            text: `${a} + ${b} = ${result}`,
          },
        ],
      }
    }
    case "multiply": {
      const a = args?.a as number
      const b = args?.b as number
      if (typeof a !== "number" || typeof b !== "number") {
        throw new McpError(ErrorCode.InvalidParams, "参数必须是数字")
      }
      const result = a * b
      return {
        content: [
          {
            type: "text",
            text: `${a} × ${b} = ${result}`,
          },
        ],
      }
    }
    default:
      throw new McpError(ErrorCode.MethodNotFound, `未知工具: ${name}`)
  }
})

// 启动服务器
async function main() {
  const transport = new StdioServerTransport()
  await server.connect(transport)
  console.error("Calculator MCP Server started")
}

main().catch((error) => {
  console.error("Server error:", error)
  process.exit(1)
})
