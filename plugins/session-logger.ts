/**
 * Session Logger Plugin
 * 
 * 一个简单的 OpenCode 插件，用于记录会话事件。
 * 当会话完成（进入空闲状态）时，会记录一条日志。
 */

import type { Plugin } from "@opencode-ai/plugin"

export const SessionLoggerPlugin: Plugin = async ({ client, project }) => {
  await client.app.log({
    body: {
      service: "session-logger",
      level: "info",
      message: "Plugin initialized",
      extra: { project: project?.name || "unknown" },
    },
  })

  return {
    // 监听会话空闲事件
    "session.idle": async ({ event }) => {
      await client.app.log({
        body: {
          service: "session-logger",
          level: "info",
          message: "Session completed",
          extra: {
            sessionId: event.sessionId,
            timestamp: new Date().toISOString(),
          },
        },
      })
    },

    // 监听文件编辑事件
    "file.edited": async ({ event }) => {
      await client.app.log({
        body: {
          service: "session-logger",
          level: "debug",
          message: "File edited",
          extra: {
            path: event.path,
          },
        },
      })
    },
  }
}

export default SessionLoggerPlugin
