/**
 * 工具守卫插件
 * 
 * 功能：在工具执行前后进行拦截，实现权限控制和日志记录
 * 
 * 使用场景：
 * - 阻止危险操作（如删除文件）
 * - 记录所有工具调用
 * - 修改工具输入参数
 */

import type { Plugin } from "@opencode-ai/plugin"

export const ToolGuardPlugin: Plugin = async ({ client }) => {
  // 危险命令黑名单
  const dangerousCommands = ["rm -rf", "sudo", "chmod 777", ":(){:|:&};:"]
  
  // 受保护文件列表
  const protectedFiles = [".env", "credentials.json", "secrets.yaml"]

  return {
    // 工具执行前钩子
    "tool.execute.before": async (input, output) => {
      const toolName = input.tool
      
      // 记录工具调用
      await client.app.log({
        body: {
          service: "tool-guard",
          level: "info",
          message: `Tool called: ${toolName}`,
          extra: { args: output.args },
        },
      })

      // 检查 Bash 命令
      if (toolName === "bash") {
        const command = output.args.command as string
        
        for (const dangerous of dangerousCommands) {
          if (command.includes(dangerous)) {
            throw new Error(`Blocked dangerous command: ${dangerous}`)
          }
        }
      }

      // 检查文件读取
      if (toolName === "read") {
        const filePath = output.args.filePath as string
        
        for (const protected of protectedFiles) {
          if (filePath.includes(protected)) {
            throw new Error(`Access denied to protected file: ${protected}`)
          }
        }
      }
    },

    // 工具执行后钩子
    "tool.execute.after": async (input, output) => {
      await client.app.log({
        body: {
          service: "tool-guard",
          level: "debug",
          message: `Tool completed: ${input.tool}`,
          extra: { 
            success: !output.error,
            duration: output.duration,
          },
        },
      })
    },
  }
}

export default ToolGuardPlugin
