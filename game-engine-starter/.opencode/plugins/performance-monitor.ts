/**
 * 游戏性能监控插件
 * 
 * 功能：监控和分析游戏性能
 */

import type { Plugin } from "@opencode-ai/plugin"

export const PerformanceMonitorPlugin: Plugin = async ({ client }) => {
  return {
    // Shell 命令执行前注入性能监控环境变量
    "shell.env": async (input, output) => {
      // 启用 Python 性能分析
      output.env.PYTHONPROFILEIMPORTTIME = "1"
    },

    // 工具执行后记录性能日志
    "tool.execute.after": async (input, output) => {
      if (input.tool === "bash" && output.duration) {
        const duration = output.duration
        
        // 记录超过 1 秒的操作
        if (duration > 1000) {
          await client.app.log({
            body: {
              service: "performance-monitor",
              level: "warn",
              message: "Slow operation detected",
              extra: {
                tool: input.tool,
                duration: `${duration}ms`,
              },
            },
          })
        }
      }
    },
  }
}

export default PerformanceMonitorPlugin
