# OpenCode 插件开发指南

## 概述

OpenCode 插件是 TypeScript/JavaScript 模块，可以扩展 OpenCode 的功能。

## 接入方式

### 1. 本地文件

将插件文件放到插件目录：

```bash
# 项目级（推荐，可提交到 Git）
.opencode/plugins/my-plugin.ts

# 全局级（个人配置）
~/.config/opencode/plugins/my-plugin.ts
```

### 2. npm 包

在 `opencode.json` 中配置：

```json
{
  "plugin": ["my-org/opencode-plugin", "npm-package-name"]
}
```

## 功能

### 1. 事件钩子

监听 OpenCode 内部事件：

```typescript
export const MyPlugin: Plugin = async () => {
  return {
    // 工具执行前
    "tool.execute.before": async (input, output) => {
      // input.tool - 工具名称
      // output.args - 工具参数
      // 可以修改 output.args 或抛出错误来阻止执行
    },
    
    // 工具执行后
    "tool.execute.after": async (input, output) => {
      // output.result - 执行结果
      // output.error - 错误信息（如果有）
    },
    
    // Shell 环境变量
    "shell.env": async (input, output) => {
      output.env.MY_VAR = "value"
    },
    
    // 会话事件
    "session.idle": async ({ event }) => {
      // 会话完成
    },
    
    "session.error": async ({ event }) => {
      // 会话错误
    },
    
    // 文件事件
    "file.edited": async ({ event }) => {
      // 文件被编辑
    },
  }
}
```

### 2. 自定义工具

添加新的工具供 LLM 使用：

```typescript
import { tool } from "@opencode-ai/plugin"

export const MyPlugin: Plugin = async () => {
  return {
    tool: {
      myTool: tool({
        description: "工具描述",
        args: {
          param1: tool.schema.string().describe("参数说明"),
          param2: tool.schema.number().optional(),
        },
        async execute(args, context) {
          return `结果: ${args.param1}`
        },
      }),
    },
  }
}
```

### 3. 日志记录

使用结构化日志：

```typescript
export const MyPlugin: Plugin = async ({ client }) => {
  await client.app.log({
    body: {
      service: "my-plugin",
      level: "info", // debug, info, warn, error
      message: "日志消息",
      extra: { key: "value" },
    },
  })
}
```

## 推进过程

### 步骤 1: 创建插件文件

```bash
mkdir -p .opencode/plugins
touch .opencode/plugins/my-plugin.ts
```

### 步骤 2: 编写插件代码

```typescript
import type { Plugin } from "@opencode-ai/plugin"

export const MyPlugin: Plugin = async ({ project, client }) => {
  console.log(`Plugin loaded for project: ${project?.name}`)
  
  return {
    "tool.execute.before": async (input, output) => {
      // 你的逻辑
    },
  }
}

export default MyPlugin
```

### 步骤 3: 测试插件

重启 OpenCode，插件会自动加载。

### 步骤 4: 调试

使用 `console.error()` 输出调试信息（会显示在 OpenCode 日志中）。

## 卡点与解决方案

### 1. 类型定义缺失

**问题**: TypeScript 报错找不到 `@opencode-ai/plugin`

**解决**: 
```bash
bun add -d @opencode-ai/plugin
# 或使用 any 类型临时解决
```

### 2. 插件不生效

**问题**: 修改插件后没有变化

**解决**: 重启 OpenCode，插件在启动时加载

### 3. 钩子不触发

**问题**: 钩子函数没有被调用

**解决**: 
- 检查钩子名称拼写
- 确保返回了正确的对象结构
- 查看控制台错误日志

### 4. 异步操作失败

**问题**: async/await 不工作

**解决**: 确保所有异步操作都正确处理了错误

## 示例插件

### 环境变量注入

```typescript
export const EnvPlugin: Plugin = async () => ({
  "shell.env": async (_, output) => {
    output.env.NODE_ENV = "development"
  },
})
```

### 阻止危险命令

```typescript
export const SafetyPlugin: Plugin = async () => ({
  "tool.execute.before": async (input, output) => {
    if (input.tool === "bash") {
      const cmd = output.args.command as string
      if (cmd.includes("rm -rf /")) {
        throw new Error("Dangerous command blocked!")
      }
    }
  },
})
```

## 最佳实践

1. **错误处理**: 所有钩子都应该有 try-catch
2. **性能**: 避免在钩子中执行耗时操作
3. **日志**: 使用 `client.app.log()` 而不是 `console.log()`
4. **命名**: 使用有意义的插件和工具名称
5. **文档**: 为插件添加 JSDoc 注释
