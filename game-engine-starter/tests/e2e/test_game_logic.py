"""
游戏逻辑测试示例

运行: pytest tests/e2e/test_game_logic.py -v
"""

import pytest


class TestMovement:
    """移动测试"""
    
    def test_game_pause_resume(self, paused_game):
        """测试：游戏暂停/恢复"""
        client = paused_game
        
        # 游戏已暂停
        result = client.state_get("is_paused")
        # 注意：具体属性名取决于你的游戏实现
        
        # 恢复游戏
        client.game_resume()
    
    def test_game_step(self, paused_game):
        """测试：单步执行"""
        client = paused_game
        
        # 执行一帧
        result = client.game_step(dt=0.016)
        
        assert result.success
        assert result.result["stepped"] == True
    
    def test_multiple_steps(self, paused_game):
        """测试：多步执行"""
        client = paused_game
        
        # 执行 60 帧
        for _ in range(60):
            result = client.game_step(dt=0.016)
            assert result.success


class TestInput:
    """输入测试"""
    
    def test_key_tap(self, game_client):
        """测试：按键点击"""
        result = game_client.input_key("SPACE", action="tap")
        
        assert result.success
    
    def test_key_press_release(self, game_client):
        """测试：按键按下和释放"""
        # 按下
        result = game_client.input_key("RIGHT", action="press")
        assert result.success
        
        # 释放
        result = game_client.input_key("RIGHT", action="release")
        assert result.success
    
    def test_multiple_keys(self, game_client):
        """测试：多键输入"""
        # 同时按下多个键
        game_client.input_key("UP", action="press")
        game_client.input_key("LEFT", action="press")
        
        # 执行一帧
        game_client.game_step(dt=0.016)
        
        # 释放
        game_client.input_key("UP", action="release")
        game_client.input_key("LEFT", action="release")


class TestPerformance:
    """性能测试"""
    
    def test_fps_under_load(self, game_client):
        """测试：负载下的 FPS"""
        # 创建 100 个实体
        for _ in range(100):
            game_client.entity_create("Enemy")
        
        # 执行 10 帧
        for _ in range(10):
            game_client.game_step(dt=0.016)
        
        # 获取 FPS
        result = game_client.perf_fps()
        
        assert result.success
        print(f"FPS: {result.result['fps']}")
    
    def test_render_count(self, game_client):
        """测试：渲染统计"""
        result = game_client.render_count()
        
        assert result.success
        print(f"Draw calls: {result.result['draw_calls']}")


class TestGameFlow:
    """游戏流程测试"""
    
    def test_complete_level_flow(self, paused_game):
        """测试：完整关卡流程（示例）"""
        client = paused_game
        
        # 1. 创建玩家
        player = client.entity_create(
            "Player",
            components=[
                {"type": "Transform", "params": {"x": 0, "y": 0}},
                {"type": "Health", "params": {"hp": 100}},
            ]
        )
        assert player.success
        player_id = player.result["entity_id"]
        
        # 2. 模拟移动
        client.input_key("RIGHT", action="press")
        for _ in range(30):  # 0.5秒
            client.game_step(dt=0.016)
        client.input_key("RIGHT", action="release")
        
        # 3. 验证玩家位置变化
        transform = client.component_get(player_id, "Transform")
        print(f"Player position: {transform.result}")
        
        # 4. 模拟跳跃
        client.input_key("SPACE", action="tap")
        client.game_step(dt=0.1)
        
        # 5. 验证状态
        # ...
