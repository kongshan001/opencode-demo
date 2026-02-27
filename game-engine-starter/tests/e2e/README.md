# tests/e2e 目录说明

## 目录结构

```
tests/e2e/
├── conftest.py          # Pytest 配置和 Fixtures
├── launcher.py          # 游戏启动器
├── client.py            # 测试客户端
├── test_basic.py        # 基础测试
├── test_game_logic.py   # 游戏逻辑测试
└── test_ui.py           # UI 交互测试
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
pytest tests/e2e/test_ui.py -v

# 带日志输出
pytest tests/e2e -v -s
```

## 编写测试

### 基础示例

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

### UI 交互示例

```python
def test_click_item(game_client):
    """测试：点击道具"""
    # 方式1：通过路径点击
    result = game_client.ui_click(path="inventory_panel/item_slot_0")
    assert result.success
    
    # 方式2：通过名称点击
    result = game_client.ui_click(name="确认按钮")
    assert result.success
    
    # 方式3：通过坐标点击
    result = game_client.ui_click_at(x=400, y=300)
    assert result.success

def test_use_item(game_client):
    """测试：使用道具"""
    # 获取道具信息
    info = game_client.item_get_info(slot_index=0)
    print(f"道具: {info.result['item']}")
    
    # 使用道具
    result = game_client.item_use(slot_index=0)
    assert result.success
```

## 可用指令

### 实体操作

| 指令 | 方法 | 说明 |
|------|------|------|
| entity.create | `entity_create(type, components)` | 创建实体 |
| entity.get | `entity_get(id)` | 获取实体 |
| entity.list | `entity_list()` | 列出实体 |

### 组件操作

| 指令 | 方法 | 说明 |
|------|------|------|
| component.get | `component_get(id, type)` | 获取组件 |
| component.set | `component_set(id, type, props)` | 设置组件 |

### 游戏控制

| 指令 | 方法 | 说明 |
|------|------|------|
| game.pause | `game_pause()` | 暂停游戏 |
| game.resume | `game_resume()` | 恢复游戏 |
| game.step | `game_step(dt)` | 单步执行 |

### 状态操作

| 指令 | 方法 | 说明 |
|------|------|------|
| state.get | `state_get(key)` | 获取状态 |
| state.set | `state_set(key, value)` | 设置状态 |

### 输入操作

| 指令 | 方法 | 说明 |
|------|------|------|
| input.key | `input_key(key, action)` | 模拟按键 |

### UI 操作

| 指令 | 方法 | 说明 |
|------|------|------|
| ui.click | `ui_click(id=None, name=None, path=None)` | 点击 UI 元素 |
| ui.click_at | `ui_click_at(x, y)` | 点击坐标 |
| ui.get_element | `ui_get_element(id=None, name=None, path=None)` | 获取元素信息 |
| ui.list_elements | `ui_list_elements()` | 列出所有元素 |
| ui.get_hierarchy | `ui_get_hierarchy()` | 获取 UI 层级 |
| ui.wait_for_element | `ui_wait_for_element(name, timeout)` | 等待元素出现 |

### 道具操作

| 指令 | 方法 | 说明 |
|------|------|------|
| item.use | `item_use(slot_index=None, item_id=None)` | 使用道具 |
| item.get_info | `item_get_info(slot_index=None, item_id=None)` | 获取道具信息 |
| item.equip | `item_equip(item_id)` | 装备道具 |
| item.drop | `item_drop(item_id)` | 丢弃道具 |

### 性能统计

| 指令 | 方法 | 说明 |
|------|------|------|
| perf.fps | `perf_fps()` | 获取 FPS |
| render.count | `render_count()` | 渲染统计 |

---

## 游戏端对接

### UI 管理器

游戏需要实现 `UIManager` 并挂载到 `game.ui_manager`：

```python
from engine.ui import UIManager, Button, InventoryPanel

class MyGame:
    def __init__(self):
        # 创建 UI 管理器
        self.ui_manager = UIManager()
        
        # 创建 UI 元素
        self.inventory = InventoryPanel()
        self.ui_manager.register(self.inventory)
        
        # 创建按钮
        self.btn_start = Button("btn_start", "开始游戏", self._on_start)
        self.ui_manager.register(self.btn_start)
```

### UI 元素

每个 UI 元素需要实现：

```python
class UIElement:
    element_id: str      # 唯一 ID
    name: str            # 可读名称
    x, y: int            # 位置
    width, height: int   # 大小
    visible: bool        # 是否可见
    enabled: bool        # 是否可交互
    
    def click(self):     # 点击事件处理
        pass
    
    def to_dict(self):   # 序列化
        return {...}
```

### 道具系统

如果需要道具操作，游戏需要实现：

```python
class MyGame:
    def use_item(self, item_id):
        # 使用道具逻辑
        pass
    
    def equip_item(self, item_id):
        # 装备道具逻辑
        pass
```

---

## 完整示例

```python
# tests/e2e/test_my_game.py

def test_buy_and_use_potion(paused_game):
    """测试：购买并使用药水"""
    client = paused_game
    
    # 1. 打开商店
    client.ui_click(name="商店")
    
    # 2. 等待商店面板
    result = client.ui_wait_for_element(name="商店面板", timeout=2.0)
    assert result.result["found"]
    
    # 3. 购买药水
    client.ui_click(path="shop_panel/item_potion")
    client.ui_click(name="购买")
    
    # 4. 关闭商店
    client.ui_click(name="关闭")
    
    # 5. 打开背包
    client.input_key("I")
    
    # 6. 等待背包
    result = client.ui_wait_for_element(name="背包", timeout=2.0)
    assert result.result["found"]
    
    # 7. 使用药水
    client.item_use(slot_index=0)
    
    # 8. 验证血量增加
    # ...
```
