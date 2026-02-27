/**
 * 通知插件
 * 
 * 功能：在特定事件发生时发送通知
 * 
 * 使用场景：
 * - 会话完成时通知用户
 * - 任务失败时告警
 * - 长时间操作完成后提醒
 */

import type { Plugin } from "@opencode-ai/plugin"

export const NotificationPlugin: Plugin = async ({ client, $ }) => {
  return {
    // 会话空闲（完成）时触发
    "session.idle": async ({ event }) => {
      // macOS 通知
      try {
        await $`osascript -e 'display notification "OpenCode 会话已完成" with title "OpenCode"'`
      } catch {
        // Linux 通知
        try {
          await $`notify-send "OpenCode" "会话已完成"`
        } catch {
          // 忽略通知失败
        }
      }
      
      await client.app.log({
        body: {
          service: "notification",
          level: "info",
          message: "Session idle notification sent",
        },
      })
    },

    // 会话错误时触发
    "session.error": async ({ event }) => {
      await client.app.log({
        body: {
          service: "notification",
          level: "error",
          message: "Session error occurred",
          extra: { error: event.error },
        },
      })
    },
  }
}

export default NotificationPlugin
