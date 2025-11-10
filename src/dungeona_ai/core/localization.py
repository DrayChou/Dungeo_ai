#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地化模块 - 支持多语言切换
"""

import yaml
import os
from typing import Dict, Any, Optional


class Localization:
    """本地化类，负责加载和管理多语言翻译"""

    def __init__(self, lang: Optional[str] = None):
        """
        初始化本地化系统

        Args:
            lang: 语言代码，如 'zh_CN', 'en'。如果为 None，则自动检测系统语言
        """
        self.lang = self._detect_language(lang)
        self.translations = {}
        self._load_translations()

    def _detect_language(self, lang: Optional[str]) -> str:
        """检测系统语言或使用指定的语言"""
        if lang:
            return lang

        # 简单的语言检测逻辑
        import locale
        try:
            system_lang = locale.getdefaultlocale()[0]
            if system_lang:
                if system_lang.startswith('zh'):
                    return 'zh_CN'
                elif system_lang.startswith('en'):
                    return 'en'
        except:
            pass

        return 'en'  # 默认英文

    def _load_translations(self) -> None:
        """加载翻译文件"""
        locale_file = os.path.join('locales', f'{self.lang}.yml')

        if not os.path.exists(locale_file):
            # 如果指定语言文件不存在，回退到英文
            if self.lang != 'en':
                print(f"警告：语言文件 {locale_file} 不存在，使用英文")
                self.lang = 'en'
                locale_file = os.path.join('locales', 'en.yml')

            # 如果英文文件也不存在，创建空翻译
            if not os.path.exists(locale_file):
                print(f"警告：语言文件 {locale_file} 不存在，使用空翻译")
                self.translations = {}
                return

        try:
            with open(locale_file, 'r', encoding='utf-8') as f:
                self.translations = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"错误：加载语言文件失败 {e}")
            self.translations = {}

    def t(self, key: str, **kwargs) -> str:
        """
        获取翻译文本

        Args:
            key: 翻译键，支持点号分隔的嵌套键，如 'ui.game_title'
            **kwargs: 格式化参数

        Returns:
            翻译后的文本
        """
        try:
            # 支持嵌套键，如 'ui.game_title'
            keys = key.split('.')
            value = self.translations

            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    value = key
                    break

            if isinstance(value, str) and kwargs:
                return value.format(**kwargs)
            return str(value)
        except:
            return key  # 如果找不到翻译，返回键名

    def get_current_language(self) -> str:
        """获取当前语言"""
        return self.lang

    def set_language(self, lang: str) -> bool:
        """
        切换语言

        Args:
            lang: 语言代码，如 'zh_CN', 'en'

        Returns:
            bool: 切换是否成功
        """
        old_lang = self.lang
        self.lang = lang
        self._load_translations()

        # 如果加载失败，回退到原语言
        if not self.translations:
            self.lang = old_lang
            self._load_translations()
            return False

        return True

    def get_available_languages(self) -> Dict[str, str]:
        """获取可用的语言列表"""
        languages = {}
        locales_dir = 'locales'

        if not os.path.exists(locales_dir):
            return languages

        try:
            for file in os.listdir(locales_dir):
                if file.endswith('.yml'):
                    lang_code = file[:-4]  # 移除 .yml 后缀
                    try:
                        with open(os.path.join(locales_dir, file), 'r', encoding='utf-8') as f:
                            data = yaml.safe_load(f) or {}
                            meta = data.get('meta', {})
                            name = meta.get('name', lang_code)
                            languages[lang_code] = name
                    except:
                        languages[lang_code] = lang_code
        except Exception as e:
            print(f"错误：扫描语言文件失败 {e}")

        return languages


# 全局本地化实例
_localization = None


def init_localization(lang: Optional[str] = None) -> None:
    """初始化本地化系统"""
    global _localization
    _localization = Localization(lang)


def t(key: str, **kwargs) -> str:
    """获取翻译文本的便捷函数"""
    global _localization
    if _localization is None:
        init_localization()
    return _localization.t(key, **kwargs)


def get_current_language() -> str:
    """获取当前语言的便捷函数"""
    global _localization
    if _localization is None:
        init_localization()
    return _localization.get_current_language()


def set_language(lang: str) -> bool:
    """切换语言的便捷函数"""
    global _localization
    if _localization is None:
        init_localization()
    return _localization.set_language(lang)


def get_dm_system_prompt(genre: str = "", character_name: str = "", role: str = "") -> str:
    """获取DM系统提示的便捷函数"""
    global _localization
    if _localization is None:
        init_localization()
    prompt = t("dm_system_prompt")

    # 如果提供了游戏信息，格式化提示
    if genre or character_name or role:
        try:
            prompt = prompt.format(
                genre=genre,
                character_name=character_name,
                role=role
            )
        except:
            pass  # 如果格式化失败，返回原始提示

    return prompt


def get_available_languages() -> Dict[str, str]:
    """获取可用语言列表的便捷函数"""
    global _localization
    if _localization is None:
        init_localization()
    return _localization.get_available_languages()