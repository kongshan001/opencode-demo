/**
 * 环境变量注入插件
 * 
 * 功能：将自定义环境变量注入到所有 Shell 执行中
 * 
 * 使用场景：
 * - 自动注入 API 密钥
 * - 设置项目特定的环境变量
 * - 配置开发/生产环境标识
 */

import type { Plugin } from "@opencode-ai/plugin"

export const EnvInjectionPlugin: Plugin = async () => {
  return {
    // shell.env 钩子会在所有 Shell 命令执行前触发
    "shell.env": async (input, output) => {
      // 注入自定义环境变量
      output.env.NODE_ENV = "development"
      output.env.PROJECT_ROOT = input.cwd
      
      // 可以注入 API 密钥（实际使用时建议从安全存储读取）
      // output.env.MY_API_KEY = "secret-key"
      
      console.error("[EnvInjection] Environment variables injected")
    },
  }
}

export default EnvInjectionPlugin
