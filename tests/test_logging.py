#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的共享日志系统
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dungeona_ai.core.logger import GameLogger
import time

def test_logging_system():
    """测试所有日志功能"""
    print("=== 测试共享日志系统 ===\n")

    # 创建日志器
    logger = GameLogger("test_error_log.txt")

    print("1. 测试错误日志...")
    logger.log_error("这是一个测试错误", Exception("测试异常"), {"test_param": "test_value"})

    print("2. 测试操作日志...")
    logger.log_operation("test_operation", {"param1": "value1", "param2": "value2"}, "操作成功", 1.234)

    print("3. 测试AI请求日志...")
    test_prompt = "这是一个测试提示，包含完整的对话内容..."
    test_request = {
        "model": "test_model",
        "prompt": test_prompt,
        "options": {"temperature": 0.8}
    }
    test_response = {
        "response": "这是一个测试AI回复，包含完整内容...",
        "thinking": "这是AI的思考过程..."
    }
    logger.log_ai_request(test_prompt, test_request, test_response, 2.567)

    print("4. 测试游戏行为日志...")
    test_conversation = """
    ### Adventure Setting ###
    Genre: Fantasy
    Player Character: TestHero the Peasant
    Starting Scenario: You're working in the fields when...

    Dungeon Master: The soil beneath your feet begins to glow...
    Player: 探索周围环境
    Dungeon Master: As you explore, you discover...
    """

    logger.log_game_action("player_input", {
        "input_length": 6,
        "input_type": "game_action",
        "raw_input": "探索周围环境"
    }, test_conversation)

    print("✅ 所有日志测试完成！")
    print("请检查以下日志文件：")
    print("- test_error_log.txt (错误日志)")
    print("- logs/operation_log.txt (操作日志)")
    print("- logs/ai_log.txt (AI请求日志)")
    print("- logs/game_log.txt (游戏行为日志)")

if __name__ == "__main__":
    test_logging_system()