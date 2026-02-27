"""
游戏集成示例

将此代码复制到你的游戏入口文件（如 main.py）
"""

from engine.testing.socket_server import GameTestServer
from engine.testing.config import TestModeConfig


def integrate_test_server(game_class):
    """
    装饰器：为游戏类添加测试服务器支持
    
    使用方法:
        @integrate_test_server
        class MyGame:
            def run(self):
                ...
    """
    original_init = game_class.__init__
    original_run = getattr(game_class, 'run', None)
    
    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.test_server = None
    
    def run(self):
        # 检查测试模式
        config = TestModeConfig.from_file()
        if not config.enabled:
            config = TestModeConfig.from_env()
        
        # 启动测试服务器
        if config.enabled:
            print(f"[Game] Test mode enabled: {config}")
            self.test_server = GameTestServer(self, port=config.port)
            self.test_server.start()
        
        try:
            # 调用原始 run 方法
            if original_run:
                original_run(self)
        finally:
            # 清理
            if self.test_server:
                self.test_server.stop()
            
            # 删除配置文件
            import os
            if os.path.exists("test_mode.json"):
                try:
                    os.remove("test_mode.json")
                except:
                    pass
    
    game_class.__init__ = __init__
    if original_run:
        game_class.run = run
    
    return game_class


# ============================================================
# 手动集成方式
# ============================================================

def manual_integration_example():
    """
    手动集成示例
    
    将以下代码添加到你的 main.py 中
    """
    
    # === 在文件开头导入 ===
    # from engine.testing.socket_server import GameTestServer
    # from engine.testing.config import TestModeConfig
    
    # === 在游戏类或 main 函数中 ===
    
    # 1. 创建游戏
    # game = MyGame()
    
    # 2. 检查测试模式
    # config = TestModeConfig.from_file()
    # if not config.enabled:
    #     config = TestModeConfig.from_env()
    
    # 3. 启动测试服务器
    # test_server = None
    # if config.enabled:
    #     test_server = GameTestServer(game, port=config.port)
    #     test_server.start()
    
    # 4. 运行游戏
    # try:
    #     game.run()
    # finally:
    #     if test_server:
    #         test_server.stop()
    pass


# ============================================================
# 完整示例
# ============================================================

if __name__ == "__main__":
    # 示例游戏类
    class ExampleGame:
        def __init__(self):
            self.is_running = False
            self.is_paused = False
            self.entities = []
            self.fps = 60
            self.renderer = type('Renderer', (), {'draw_count': 0})()
        
        def create_entity(self, entity_type):
            entity = type('Entity', (), {
                'id': len(self.entities),
                'is_active': True,
                'components': {}
            })()
            self.entities.append(entity)
            return entity
        
        def get_entity(self, entity_id):
            for e in self.entities:
                if e.id == entity_id:
                    return e
            return None
        
        def pause(self):
            self.is_paused = True
            print("[Game] Paused")
        
        def resume(self):
            self.is_paused = False
            print("[Game] Resumed")
        
        def step(self, dt):
            print(f"[Game] Step: dt={dt}")
        
        def run(self):
            import time
            self.is_running = True
            print("[Game] Running...")
            
            while self.is_running:
                if not self.is_paused:
                    pass  # 游戏逻辑
                time.sleep(0.016)
    
    # 使用装饰器集成
    ExampleGame = integrate_test_server(ExampleGame)
    
    # 运行
    game = ExampleGame()
    game.run()
