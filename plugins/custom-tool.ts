/**
 * 自定义工具插件
 * 
 * 功能：为 OpenCode 添加自定义工具
 * 
 * 使用场景：
 * - 添加项目特定的工具
 * - 封装常用操作
 * - 集成外部服务
 */

import { type Plugin, tool } from "@opencode-ai/plugin"

export const CustomToolsPlugin: Plugin = async (ctx) => {
  return {
    tool: {
      // 时间戳工具
      timestamp: tool({
        description: "获取当前时间戳，支持多种格式",
        args: {
          format: tool.schema.enum(["unix", "iso", "locale"]).optional().default("iso"),
        },
        async execute(args, context) {
          const now = new Date()
          
          switch (args.format) {
            case "unix":
              return `Unix timestamp: ${Math.floor(now.getTime() / 1000)}`
            case "iso":
              return `ISO 8601: ${now.toISOString()}`
            case "locale":
              return `Locale string: ${now.toLocaleString()}`
            default:
              return now.toString()
          }
        },
      }),

      // JSON 格式化工具
      jsonFormat: tool({
        description: "格式化 JSON 字符串",
        args: {
          json: tool.schema.string().describe("要格式化的 JSON 字符串"),
          indent: tool.schema.number().optional().default(2).describe("缩进空格数"),
        },
        async execute(args, context) {
          try {
            const parsed = JSON.parse(args.json)
            return JSON.stringify(parsed, null, args.indent)
          } catch (error) {
            return `Error: Invalid JSON - ${error}`
          }
        },
      }),

      // Base64 编码工具
      base64Encode: tool({
        description: "将字符串编码为 Base64",
        args: {
          text: tool.schema.string().describe("要编码的文本"),
        },
        async execute(args, context) {
          const encoded = Buffer.from(args.text).toString("base64")
          return `Base64 encoded: ${encoded}`
        },
      }),

      // Base64 解码工具
      base64Decode: tool({
        description: "将 Base64 字符串解码",
        args: {
          encoded: tool.schema.string().describe("要解码的 Base64 字符串"),
        },
        async execute(args, context) {
          try {
            const decoded = Buffer.from(args.encoded, "base64").toString("utf-8")
            return `Decoded: ${decoded}`
          } catch (error) {
            return `Error: Invalid Base64 - ${error}`
          }
        },
      }),
    },
  }
}

export default CustomToolsPlugin
