# tests/e2e 目录说明

## 目录结构

```
tests/e2e/
├── conftest.py          # Pytest 配置和 Fixtures
├── launcher.py          # 游戏启动器
├── client.py            # 测试客户端
├── test_basic.py        # 基础测试
└── test_game_logic.py   # 游戏逻辑测试
```

## 配置

在 `conftest.py` 中修改：

```python
# exe 文件路径
EXE_PATH = r"D:\mygame\mygame.exe"

# Socket 端口
PORT = 9876
```

## 运行测试

```bash
# 运行所有 E2E 测试
pytest tests/e2e -v

# 运行特定测试
pytest tests/e2e/test_basic.py -v

# 带日志输出
pytest tests/e2e -v -s
```

## 编写测试

```python
def test_my_feature(game_client):
    """测试我的功能"""
    # 1. 创建实体
    result = game_client.entity_create("Player")
    assert result.success
    
    # 2. 获取实体 ID
    entity_id = result.result["entity_id"]
    
    # 3. 操作实体
    game_client.component_set(entity_id, "Transform", {"x": 100})
    
    # 4. 验证结果
    transform = game_client.component_get(entity_id, "Transform")
    assert transform.result["x"] == 100
```

## 可用指令

| 指令 | 方法 | 说明 |
|------|------|------|
| entity.create | `entity_create()` | 创建实体 |
| entity.get | `entity_get(id)` | 获取实体 |
| entity.list | `entity_list()` | 列出实体 |
| component.get | `component_get(id, type)` | 获取组件 |
| component.set | `component_set(id, type, props)` | 设置组件 |
| game.pause | `game_pause()` | 暂停游戏 |
| game.resume | `game_resume()` | 恢复游戏 |
| game.step | `game_step(dt)` | 单步执行 |
| state.get | `state_get(key)` | 获取状态 |
| state.set | `state_set(key, value)` | 设置状态 |
| input.key | `input_key(key, action)` | 模拟按键 |
| perf.fps | `perf_fps()` | 获取 FPS |
| render.count | `render_count()` | 渲染统计 |
