/**
 * Python 代码保护插件
 * 
 * 功能：防止危险操作，保护敏感文件
 */

import type { Plugin } from "@opencode-ai/plugin"

export const PythonGuardPlugin: Plugin = async ({ client }) => {
  // 危险 Python 命令模式
  const dangerousPatterns = [
    /import\s+os\s*;\s*os\.system\s*\(/,
    /exec\s*\(\s*['"]/,
    /eval\s*\(\s*['"]/,
    /__import__\s*\(\s*['"]/,
    /subprocess\.call\s*\([^)]*shell\s*=\s*True/,
    /pickle\.loads\s*\(/,
    /yaml\.load\s*\([^)]*\)\s*(?!Loader)/,
  ]

  // 受保护的文件
  const protectedFiles = [
    "secrets.py",
    "credentials.py",
    ".env",
    "config.local.py",
    "private_key",
  ]

  return {
    "tool.execute.before": async (input, output) => {
      // 检查 Bash 命令
      if (input.tool === "bash") {
        const command = output.args.command as string
        
        // 检查危险模式
        for (const pattern of dangerousPatterns) {
          if (pattern.test(command)) {
            await client.app.log({
              body: {
                service: "python-guard",
                level: "warn",
                message: "Potentially dangerous Python code blocked",
              },
            })
            throw new Error(`Blocked potentially dangerous Python code pattern`)
          }
        }
      }

      // 检查文件操作
      if (input.tool === "read" || input.tool === "write" || input.tool === "edit") {
        const filePath = (output.args.filePath || output.args.file_path || "") as string
        
        for (const protected of protectedFiles) {
          if (filePath.includes(protected)) {
            await client.app.log({
              body: {
                service: "python-guard",
                level: "warn",
                message: `Access to protected file blocked: ${protected}`,
              },
            })
            throw new Error(`Access denied to protected file: ${protected}`)
          }
        }
      }
    },
  }
}

export default PythonGuardPlugin
