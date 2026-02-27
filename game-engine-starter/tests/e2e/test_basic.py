"""
基础 E2E 测试示例

运行: pytest tests/e2e/test_basic.py -v
"""

import pytest


class TestGameBasic:
    """游戏基础功能测试"""
    
    def test_game_starts(self, game_client):
        """测试：游戏能启动"""
        result = game_client.state_get()
        assert result.success, f"Failed to get state: {result.error}"
    
    def test_fps_reporting(self, game_client):
        """测试：FPS 报告正常"""
        result = game_client.perf_fps()
        
        assert result.success
        assert "fps" in result.result
    
    def test_entity_list(self, game_client):
        """测试：实体列表功能"""
        result = game_client.entity_list()
        
        assert result.success
        assert "count" in result.result


class TestEntity:
    """实体测试"""
    
    def test_entity_create(self, game_client):
        """测试：创建实体"""
        result = game_client.entity_create("Player")
        
        assert result.success
        assert "entity_id" in result.result
    
    def test_entity_create_with_components(self, game_client):
        """测试：创建带组件的实体"""
        result = game_client.entity_create(
            "Player",
            components=[
                {"type": "Transform", "params": {"x": 100, "y": 200}}
            ]
        )
        
        assert result.success
        entity_id = result.result["entity_id"]
        
        # 验证组件
        transform = game_client.component_get(entity_id, "Transform")
        assert transform.success
    
    def test_entity_get(self, game_client):
        """测试：获取实体"""
        # 创建实体
        create_result = game_client.entity_create("Player")
        assert create_result.success
        
        entity_id = create_result.result["entity_id"]
        
        # 获取实体
        get_result = game_client.entity_get(entity_id)
        
        assert get_result.success
        assert get_result.result["id"] == entity_id


class TestComponent:
    """组件测试"""
    
    def test_component_set(self, game_client):
        """测试：设置组件属性"""
        # 创建实体
        result = game_client.entity_create(
            "Player",
            components=[{"type": "Transform", "params": {"x": 0, "y": 0}}]
        )
        entity_id = result.result["entity_id"]
        
        # 设置属性
        game_client.component_set(entity_id, "Transform", {"x": 100, "y": 200})
        
        # 验证
        transform = game_client.component_get(entity_id, "Transform")
        assert transform.success


class TestGameState:
    """游戏状态测试"""
    
    def test_state_set_get(self, game_client):
        """测试：状态读写"""
        # 设置状态
        game_client.state_set("test_value", 123)
        
        # 获取状态
        result = game_client.state_get("test_value")
        
        assert result.success
        assert result.result["value"] == 123
