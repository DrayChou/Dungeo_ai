"""
AI Dungeon Master Adventure - 主要包
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"
__description__ = "AI-powered interactive storytelling adventure game"

# 导出核心组件
from .core import GameLogger, GameCore, GameState, CONFIG, DM_SYSTEM_PROMPT
from .core.localization import t, get_current_language, get_available_languages
from .core.game_core import get_genre_description, get_role_starter, ROLE_STARTERS

__all__ = [
    'GameLogger', 'GameCore', 'GameState', 'CONFIG', 'DM_SYSTEM_PROMPT',
    't', 'get_current_language', 'get_available_languages',
    'get_genre_description', 'get_role_starter', 'ROLE_STARTERS'
]