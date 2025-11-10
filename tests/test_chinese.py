#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试中文本地化功能
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dungeona_ai.core.localization import t

def test_chinese_localization():
    """测试中文本地化是否正常工作"""
    print("=== 中文本地化测试 ===\n")

    # 测试游戏标题
    print("游戏标题:")
    print(t('ui.game_title'))
    print()

    # 测试基本界面文本
    print("基本界面文本测试:")
    print(f"可用命令: {t('ui.available_commands').strip().split()[0]}")
    print(f"选择类型: {t('ui.choose_genre')}")
    print(f"模型选择: {t('ui.select_model', count=3, default_model='test')}")
    print()

    # 测试游戏类型描述
    print("游戏类型描述测试:")
    from dungeona_ai.core.game_core import get_genre_description
    fantasy_desc = get_genre_description("Fantasy")
    print(f"奇幻类型: {fantasy_desc[:50]}...")
    print()

    # 测试配置值
    print("配置值测试:")
    from dungeona_ai.core.game_core import CONFIG, DM_SYSTEM_PROMPT
    print(f"默认角色名: {CONFIG.get('DEFAULT_CHARACTER_NAME', '未知')}")
    print(f"日志文件: {CONFIG['LOG_FILE']}")
    print()

    # 测试DM提示
    print("DM系统提示测试（前100字符）:")
    dm_prompt = DM_SYSTEM_PROMPT
    print(dm_prompt[:100] + "...")
    print()

    print("✅ 中文本地化测试完成！")

if __name__ == "__main__":
    test_chinese_localization()