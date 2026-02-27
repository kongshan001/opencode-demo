# OpenCode 配置指南

## 概述

OpenCode 通过 JSON 配置文件进行自定义。

## 配置文件位置

| 位置 | 作用 | 优先级 |
|------|------|--------|
| `~/.config/opencode/opencode.json` | 全局配置 | 低 |
| `opencode.json` | 项目配置 | 高 |
| `.opencode/` | 项目扩展 | 最高 |

## 核心配置

### 模型配置

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-20250514",
  "small_model": "anthropic/claude-haiku-4-20250514"
}
```

### 提供商配置

```json
{
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}",
        "timeout": 300000
      }
    }
  }
}
```

### MCP 服务器

```json
{
  "mcp": {
    "calculator": {
      "type": "local",
      "command": ["bun", "run", "./mcp-servers/calculator/index.ts"],
      "enabled": true
    },
    "remote-api": {
      "type": "remote",
      "url": "https://api.example.com/mcp",
      "headers": {
        "Authorization": "Bearer {env:API_KEY}"
      }
    }
  }
}
```

### 插件

```json
{
  "plugin": [
    "opencode-helicone-session",
    "@my-org/custom-plugin"
  ]
}
```

### 代理

```json
{
  "agent": {
    "code-reviewer": {
      "description": "代码审查专家",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-20250514",
      "tools": {
        "write": false,
        "edit": false
      }
    }
  }
}
```

### 命令

```json
{
  "command": {
    "test": {
      "template": "运行测试并分析结果",
      "description": "运行测试",
      "agent": "build"
    }
  }
}
```

### 工具权限

```json
{
  "tools": {
    "write": true,
    "bash": true,
    "webfetch": false
  }
}
```

### 权限控制

```json
{
  "permission": {
    "edit": "ask",
    "bash": {
      "git push": "ask",
      "npm *": "allow"
    }
  }
}
```

### 自定义指令

```json
{
  "instructions": [
    "CONTRIBUTING.md",
    "docs/guidelines.md",
    ".cursor/rules/*.md"
  ]
}
```

### 格式化器

```json
{
  "formatter": {
    "prettier": {
      "disabled": false
    },
    "custom": {
      "command": ["npx", "prettier", "--write", "$FILE"],
      "extensions": [".js", ".ts"]
    }
  }
}
```

### 文件监视

```json
{
  "watcher": {
    "ignore": [
      "node_modules/**",
      "dist/**",
      ".git/**"
    ]
  }
}
```

### 压缩设置

```json
{
  "compaction": {
    "auto": true,
    "prune": true,
    "reserved": 10000
  }
}
```

## 环境变量

### 在配置中使用

```json
{
  "model": "{env:OPENCODE_MODEL}",
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

### 文件内容

```json
{
  "provider": {
    "openai": {
      "options": {
        "apiKey": "{file:~/.secrets/openai-key}"
      }
    }
  }
}
```

## TUI 配置

使用单独的 `tui.json` 文件：

```json
{
  "$schema": "https://opencode.ai/tui.json",
  "theme": "tokyonight",
  "scroll_speed": 3,
  "diff_style": "auto",
  "keybinds": {}
}
```

## 服务器配置

```json
{
  "server": {
    "port": 4096,
    "hostname": "0.0.0.0",
    "mdns": true,
    "mdnsDomain": "myproject.local",
    "cors": ["http://localhost:5173"]
  }
}
```

## 完整示例

```json
{
  "$schema": "https://opencode.ai/config.json",
  
  "model": "anthropic/claude-sonnet-4-20250514",
  "small_model": "anthropic/claude-haiku-4-20250514",
  
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}"
      }
    }
  },
  
  "mcp": {
    "calculator": {
      "type": "local",
      "command": ["bun", "run", "./mcp-servers/calculator/index.ts"],
      "enabled": true
    }
  },
  
  "plugin": ["@my-org/custom-plugin"],
  
  "agent": {
    "reviewer": {
      "description": "代码审查",
      "mode": "subagent",
      "tools": {
        "write": false,
        "edit": false
      }
    }
  },
  
  "command": {
    "test": {
      "template": "运行测试",
      "description": "测试"
    }
  },
  
  "permission": {
    "edit": "ask",
    "bash": {
      "*": "ask",
      "git status": "allow"
    }
  },
  
  "instructions": ["AGENTS.md", "docs/*.md"],
  
  "autoupdate": true,
  
  "compaction": {
    "auto": true,
    "reserved": 10000
  }
}
```

## 配置优先级

从低到高：
1. 远程配置 (`.well-known/opencode`)
2. 全局配置 (`~/.config/opencode/opencode.json`)
3. 自定义配置 (`OPENCODE_CONFIG`)
4. 项目配置 (`opencode.json`)
5. `.opencode/` 目录
6. 内联配置 (`OPENCODE_CONFIG_CONTENT`)

## 最佳实践

1. **使用 Schema**: 添加 `$schema` 获得自动补全
2. **环境变量**: 敏感信息使用 `{env:VAR}`
3. **项目配置**: 团队共享的配置放在 `opencode.json`
4. **个人配置**: 个人偏好放在全局配置
5. **版本控制**: `opencode.json` 可以提交到 Git
