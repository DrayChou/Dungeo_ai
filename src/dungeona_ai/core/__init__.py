"""
核心模块 - 游戏逻辑、日志系统、本地化
"""

from .logger import GameLogger
from .localization import init_localization, t, get_current_language, get_available_languages
from .game_core import GameCore, GameState, CONFIG, DM_SYSTEM_PROMPT, get_genre_description, get_role_starter, ROLE_STARTERS

__all__ = [
    'GameLogger',
    'init_localization', 't', 'get_current_language', 'get_available_languages',
    'GameCore', 'GameState', 'CONFIG', 'DM_SYSTEM_PROMPT', 'get_genre_description', 'get_role_starter', 'ROLE_STARTERS'
]