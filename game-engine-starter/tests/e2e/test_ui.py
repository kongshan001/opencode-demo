"""
UI 交互测试示例

运行: pytest tests/e2e/test_ui.py -v
"""

import pytest


class TestUIBasics:
    """UI 基础测试"""
    
    def test_list_ui_elements(self, game_client):
        """测试：列出 UI 元素"""
        result = game_client.ui_list_elements()
        
        assert result.success
        print(f"UI 元素数量: {result.result['count']}")
        
        for elem in result.result['elements']:
            print(f"  - {elem['id']}: {elem.get('name', '')}")
    
    def test_get_ui_hierarchy(self, game_client):
        """测试：获取 UI 层级结构"""
        result = game_client.ui_get_hierarchy()
        
        assert result.success
        print(f"UI 层级: {result.result}")
    
    def test_get_element_by_id(self, game_client):
        """测试：通过 ID 获取元素"""
        result = game_client.ui_get_element(element_id="btn_start")
        
        if result.success:
            assert result.result["id"] == "btn_start"
    
    def test_get_element_by_name(self, game_client):
        """测试：通过名称获取元素"""
        result = game_client.ui_get_element(name="背包")
        
        if result.success:
            assert result.result.get("name") == "背包"


class TestUIClick:
    """UI 点击测试"""
    
    def test_click_by_id(self, game_client):
        """测试：通过 ID 点击"""
        result = game_client.ui_click(element_id="btn_start")
        
        # 结果可能是成功或失败（取决于元素是否存在）
        print(f"点击结果: {result.result}")
    
    def test_click_by_name(self, game_client):
        """测试：通过名称点击"""
        result = game_client.ui_click(name="开始游戏")
        
        print(f"点击结果: {result.result}")
    
    def test_click_by_path(self, game_client):
        """测试：通过路径点击"""
        # 点击背包中的第一个道具槽
        result = game_client.ui_click(path="inventory_panel/item_slot_0")
        
        print(f"点击结果: {result.result}")
    
    def test_click_at_coordinates(self, game_client):
        """测试：点击坐标"""
        result = game_client.ui_click_at(x=400, y=300)
        
        assert result.success
        print(f"点击的元素: {result.result.get('element')}")


class TestUIWait:
    """UI 等待测试"""
    
    def test_wait_for_element_by_name(self, game_client):
        """测试：等待元素出现"""
        result = game_client.ui_wait_for_element(name="背包", timeout=2.0)
        
        print(f"找到元素: {result.result.get('found')}")
        if result.result.get('found'):
            print(f"元素信息: {result.result.get('element')}")


class TestItemInteraction:
    """道具交互测试"""
    
    def test_get_item_info(self, game_client):
        """测试：获取道具信息"""
        result = game_client.item_get_info(slot_index=0)
        
        if result.success:
            print(f"道具槽 0: {result.result.get('item')}")
    
    def test_use_item_by_slot(self, game_client):
        """测试：使用道具（通过槽位）"""
        result = game_client.item_use(slot_index=0)
        
        print(f"使用道具结果: {result.result}")
    
    def test_use_item_by_id(self, game_client):
        """测试：使用道具（通过 ID）"""
        result = game_client.item_use(item_id="potion_hp_001")
        
        print(f"使用道具结果: {result.result}")
    
    def test_equip_item(self, game_client):
        """测试：装备道具"""
        result = game_client.item_equip(item_id="sword_001")
        
        print(f"装备道具结果: {result.result}")
    
    def test_drop_item(self, game_client):
        """测试：丢弃道具"""
        result = game_client.item_drop(item_id="junk_001")
        
        print(f"丢弃道具结果: {result.result}")


class TestComplexUIFlow:
    """复杂 UI 流程测试"""
    
    def test_complete_item_flow(self, paused_game):
        """测试：完整的道具使用流程"""
        client = paused_game
        
        # 1. 打开背包
        result = client.input_key("I")  # 假设 I 键打开背包
        assert result.success
        
        # 2. 等待背包面板出现
        result = client.ui_wait_for_element(name="背包", timeout=2.0)
        
        if result.result.get("found"):
            # 3. 获取第一个道具信息
            result = client.item_get_info(slot_index=0)
            
            if result.success and result.result.get("item"):
                item = result.result["item"]
                print(f"道具: {item}")
                
                # 4. 使用道具
                result = client.item_use(slot_index=0)
                assert result.success
    
    def test_shop_buy_flow(self, paused_game):
        """测试：商店购买流程（示例）"""
        client = paused_game
        
        # 1. 点击 NPC 打开商店
        result = client.ui_click(name="商人NPC")
        
        if result.success:
            # 2. 等待商店面板
            result = client.ui_wait_for_element(name="商店面板", timeout=2.0)
            
            if result.result.get("found"):
                # 3. 点击购买按钮
                result = client.ui_click(path="shop_panel/btn_buy")
                
                if result.success:
                    # 4. 确认购买
                    result = client.ui_click(name="确认")
                    assert result.success
    
    def test_settings_flow(self, paused_game):
        """测试：修改设置流程（示例）"""
        client = paused_game
        
        # 1. 打开设置
        result = client.ui_click(name="设置")
        
        if result.success:
            # 2. 点击音量滑块位置
            result = client.ui_click_at(x=300, y=200)
            
            if result.success:
                # 3. 保存设置
                result = client.ui_click(name="保存")
                assert result.success
