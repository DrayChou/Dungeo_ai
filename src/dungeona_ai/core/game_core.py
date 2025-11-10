#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏核心模块 - 统一管理共享的游戏逻辑、配置和功能
"""

import os
import subprocess
import datetime
import time
import json
import traceback
import requests
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

# Import localization
from .localization import init_localization, t, get_current_language
from .logger import GameLogger


# ===== INITIALIZATION =====
# Initialize localization (default to Chinese)
init_localization('zh_CN')

# ===== CONFIGURATION =====
CONFIG = {
    "ALLTALK_API_URL": "http://localhost:7851/api/tts-generate",
    "OLLAMA_URL": "http://localhost:11434/api/generate",
    "LM_STUDIO_URL": "http://localhost:11435/v1/chat/completions",
    "LOG_FILE": "error_log.txt",
    "SAVE_DIR": "saves",
    "SAVE_FILE": "adventure.txt",
    "DEFAULT_MODEL": "qwen3-vl:4b",
    "REQUEST_TIMEOUT": 180,
    "AUDIO_SAMPLE_RATE": 22050,
    "MAX_CONVERSATION_LENGTH": 10000,
    "AUTO_SAVE_INTERVAL": 300000,  # 5 minutes in milliseconds
    "CONFIG_FILE": "config.ini"
}

# ===== GAME DATA =====
@dataclass
class GameState:
    """游戏状态数据类"""
    conversation: str = ""
    last_ai_reply: str = ""
    last_player_input: str = ""
    current_model: str = CONFIG["DEFAULT_MODEL"]
    character_name: str = "亚历克斯"
    selected_genre: str = ""
    selected_role: str = ""
    adventure_started: bool = False


# ===== DM SYSTEM PROMPT =====
DM_SYSTEM_PROMPT = t("dm_system_prompt")

# ===== GENRE AND ROLE DATA =====
def get_genre_description(genre: str) -> str:
    """获取游戏类型描述"""
    descriptions = {
        "Fantasy": t("genres.fantasy"),
        "Sci-Fi": t("genres.scifi"),
        "Cyberpunk": t("genres.cyberpunk"),
        "Post-Apocalyptic": t("genres.post_apocalyptic"),
        "1880": t("genres.1880s"),
        "WW1": t("genres.ww1"),
        "1925 New York": t("genres.1925_new_york"),
        "Roman Empire": t("genres.roman_empire"),
        "French Revolution": t("genres.french_revolution")
    }
    return descriptions.get(genre, genre)

def get_role_starter(genre: str, role: str) -> str:
    """获取角色起始描述"""
    try:
        # 尝试从本地化文件获取（使用小写）
        return t(f"role_starters.{genre.lower()}.{role.lower()}")
    except:
        # 回退到默认值
        return f"You find yourself in an unexpected situation when"

# ===== ROLE STARTERS =====
# 保持原有的英文版本作为备用（如果本地化失败）
ROLE_STARTERS = {
    "Fantasy": {
        "Peasant": "You're working in the fields of a small village when",
        "Noble": "You're waking up from your bed in your mansion when",
        "Mage": "You're studying ancient tomes in your tower when",
        "Knight": "You're training in the castle courtyard when",
        "Ranger": "You're tracking animals in the deep forest when",
        "Thief": "You're casing a noble's house from an alley in a city when",
        "Bard": "You're performing in a crowded tavern when",
        "Cleric": "You're tending to the sick in the temple when",
        "Assassin": "You're preparing to attack your target in the shadows when",
        "Paladin": "You're praying at the altar of your deity when",
        "Alchemist": "You're carefully measuring reagents in your alchemy lab when",
        "Druid": "You're communing with nature in the sacred grove when",
        "Warlock": "You're negotiating with your otherworldly patron when",
        "Monk": "You're meditating in the monastery courtyard when",
        "Sorcerer": "You're struggling to control your innate magical powers when",
        "Beastmaster": "You're training your animal companions in the forest clearing when",
        "Enchanter": "You're imbuing magical properties into a mundane object when",
        "Blacksmith": "You're forging a new weapon at your anvil when",
        "Merchant": "You're haggling with customers at the marketplace when",
        "Gladiator": "You're preparing for combat in the arena when",
        "Wizard": "You're researching new spells in your arcane library when"
    },
    "Sci-Fi": {
        "Space Marine": "You're conducting patrol on a derelict space station when",
        "Scientist": "You're analyzing alien samples in your lab when",
        "Android": "You're performing system diagnostics on your ship when",
        "Pilot": "You're navigating through an asteroid field when",
        "Engineer": "You're repairing the FTL drive when",
        "Alien Diplomat": "You're negotiating with an alien delegation when",
        "Bounty Hunter": "You're tracking a target through a spaceport when",
        "Starship Captain": "You're commanding the bridge during warp travel when",
        "Space Pirate": "You're plotting your next raid from your starship's bridge when",
        "Navigator": "You're charting a course through uncharted space when",
        "Robot Technician": "You're repairing a malfunctioning android when",
        "Cybernetic Soldier": "You're calibrating your combat implants when",
        "Explorer": "You're scanning a newly discovered planet when",
        "Astrobiologist": "You're studying alien life forms in your lab when",
        "Quantum Hacker": "You're breaching a corporate firewall when",
        "Galactic Trader": "You're negotiating a deal for rare resources when",
        "AI Specialist": "You're debugging a sentient AI's personality matrix when",
        "Terraformer": "You're monitoring atmospheric changes on a new colony world when",
        "Cyberneticist": "You're installing neural enhancements in a patient when"
    },
    "Cyberpunk": {
        "Hacker": "你入侵企业网络时，突然",
        "Street Samurai": "你在霓虹灯照亮的街道上巡逻时，突然",
        "Corporate Agent": "你在高层办公室完成交易时，突然",
        "Techie": "你在工作室里修改赛博格时，突然",
        "Rebel Leader": "你策划对企业设施的突袭时，突然",
        "Cyborg": "你在校准赛博格增强物时，突然",
        "Drone Operator": "你从指挥中心控制监控无人机时，突然",
        "Synth Dealer": "你谈判非法赛博格交易时，突然",
        "Information Courier": "你穿越危险街道递送敏感数据时，突然",
        "Augmentation Engineer": "你在后巷诊所安装赛博格时，突然",
        "Black Market Dealer": "你在隐藏商店里安排违禁品时，突然",
        "Scumbag": "你在贫民窟寻找易受骗的目标时，突然",
        "Police": "你在霓虹灯浸染的街道上巡逻时，突然"
    },
    "Post-Apocalyptic": {
        "Survivor": "你在旧城市的废墟中搜寻时，突然",
        "Scavenger": "你在搜索前崩塌掩体时，突然",
        "Raider": "你在荒野中伏击车队时，突然",
        "Medic": "你在诊所里治疗辐射病时，突然",
        "Cult Leader": "你在仪式上向追随者布道时，突然",
        "Mutant": "你在定居点隐藏变异时，突然",
        "Trader": "你在荒地前哨站交易物资时，突然",
        "Berserker": "你在为下次突袭磨利武器时，突然",
        "Soldier": "你在定居点守卫抵御袭击者时，突然"
    },
    "1880": {
        "Thief": "你潜伏在城市小巷的阴影中时，突然",
        "Beggar": "你坐在寒冷街角拿着杯子时，突然",
        "Detective": "你在犯罪现场检查线索时，突然",
        "Rich Man": "你在豪华书房里享受雪茄时，突然",
        "Factory Worker": "你在嘈杂工厂里辛苦劳作时，突然",
        "Child": "你在街上玩呼啦圈时，突然",
        "Orphan": "你在垃圾桶里搜寻残羹剩饭时，突然",
        "Murderer": "你在暗巷里清洗手上的血迹时，突然",
        "Butcher": "你在柜台后磨利刀具时，突然",
        "Baker": "你在凌晨时分揉面团时，突然",
        "Banker": "你在办公室里数钱时，突然",
        "Policeman": "你在雾蒙蒙的街道上巡逻时，突然"
    },
    "WW1": {
        "Soldier (French)": "你在西线泥泞的战壕里蜷缩时，突然",
        "Soldier (English)": "你在烛光下写家信时，突然",
        "Soldier (Russian)": "你在冰冻的东线瑟瑟发抖时，突然",
        "Soldier (Italian)": "你在攀登陡峭的阿尔卑斯山坡时，突然",
        "Soldier (USA)": "你刚抵达欧洲战场时，突然",
        "Soldier (Japanese)": "你在太平洋前哨站守卫时，突然",
        "Soldier (German)": "你准备夜袭时，突然",
        "Soldier (Austrian)": "你在捍卫摇摇欲坠帝国的边境时，突然",
        "Soldier (Bulgarian)": "你在巴尔干半岛坚守防线时，突然",
        "Civilian": "你在排队领取配给面包时，突然",
        "Resistance Fighter": "你在阁楼传输加密信息时，突然"
    },
    "1925 New York": {
        "Mafia Boss": "你在后屋非法酒吧里数非法收入时，突然",
        "Drunk": "你在黎明时分踉跄走出爵士俱乐部时，突然",
        "Police Officer": "你从已知私酒贩子那里收受贿赂时，突然",
        "Detective": "你在检查黑帮谋杀现场时，突然",
        "Factory Worker": "你在生产线上组装福特T型车时，突然",
        "Bootlegger": "你在运送一批非法私酒时，突然"
    },
    "Roman Empire": {
        "Slave": "你在烈日下搬运重石时，突然",
        "Gladiator": "你在进入竞技场前磨利剑时，突然",
        "Beggar": "你在广场附近讨钱时，突然",
        "Senator": "你在库里亚策划政治操纵时，突然",
        "Imperator": "你从宫殿阳台检阅军团时，突然",
        "Soldier": "你在边境行军时，突然",
        "Noble": "你在别墅举办颓废宴会时，突然",
        "Trader": "你在市场上讨价还价香料时，突然",
        "Peasant": "你在照料贫瘠庄稼时，突然",
        "Priest": "你在寺庙里献祭山羊时，突然",
        "Barbarian": "你在莱茵河对岸磨利斧头时，突然",
        "Philosopher": "你在沉思存在的本质时，突然",
        "Mathematician": "你在计算地球周长时，突然",
        "Semi-God": "你在奥林匹斯山上引导神力时，突然"
    },
    "French Revolution": {
        "Peasant": "你拿着草叉向巴士底狱进军时，突然",
        "King": "你在巴黎挨饿时奢华进餐，突然",
        "Noble": "你向革命者隐藏家族珠宝时，突然",
        "Beggar": "你在贵族垃圾箱里翻找时，突然",
        "Soldier": "你在守卫杜伊勒里宫时，突然",
        "General": "你在策划针对叛军的部队部署时，突然",
        "Resistance": "你在秘密印刷革命小册子时，突然",
        "Politician": "你在国民大会上发表激烈演说时，突然"
    }
}


class GameCore:
    """游戏核心类，提供共享的游戏逻辑和功能"""

    def __init__(self, log_file_path: str = None):
        """
        初始化游戏核心

        Args:
            log_file_path: 日志文件路径
        """
        self.log_path = log_file_path or CONFIG["LOG_FILE"]
        self.logger = GameLogger(self.log_path)
        self.state = GameState()

    def log_error(self, error_message: str, exception: Optional[Exception] = None,
                  context: Optional[Dict[str, Any]] = None) -> None:
        """记录错误日志"""
        self.logger.log_error(error_message, exception, context)

    def log_operation(self, operation: str, parameters: dict = None, result: str = None,
                      duration: float = None, context: Optional[Dict[str, Any]] = None) -> None:
        """记录操作日志"""
        self.logger.log_operation(operation, parameters, result, duration, context)

    def log_ai_request(self, prompt: str, request_data: dict, response_data: dict,
                       duration: float, context: Optional[Dict[str, Any]] = None) -> None:
        """记录AI请求日志"""
        self.logger.log_ai_request(prompt, request_data, response_data, duration, context)

    def log_game_action(self, action: str, details: dict = None,
                       conversation: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> None:
        """记录游戏行为日志"""
        self.logger.log_game_action(action, details, conversation, context)

    def check_server(self, url: str, service_name: str) -> bool:
        """通用服务器健康检查"""
        try:
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.log_error(f"{service_name} check failed", e)
            return False

    def check_ollama_server(self) -> bool:
        """检查Ollama服务器"""
        return self.check_server("http://localhost:11434/api/tags", "Ollama")

    def check_lm_studio_server(self) -> bool:
        """检查LM Studio服务器"""
        return self.check_server("http://localhost:11435/v1/models", "LM Studio")

    def check_alltalk_server(self) -> bool:
        """检查AllTalk服务器"""
        return self.check_server("http://localhost:7851", "AllTalk")

    def detect_model_type(self, model: str) -> str:
        """
        检测模型类型

        Args:
            model: 模型名称

        Returns:
            模型类型: 'ollama', 'lm_studio', 或 'unknown'
        """
        # LM Studio模型通常包含斜杠或特定格式
        if '/' in model or any(prefix in model.lower() for prefix in ['qwen/', 'llama/', 'mistral/', 'gpt/']):
            return 'lm_studio'
        # Ollama模型通常不包含斜杠
        elif ':' in model or model.isalnum() or '-' in model:
            return 'ollama'
        else:
            # 尝试通过服务器可用性判断
            if self.check_lm_studio_server():
                return 'lm_studio'
            elif self.check_ollama_server():
                return 'ollama'
            return 'unknown'

    def get_ai_response(self, prompt: str, model: str = None, temperature: float = 0.7) -> str:
        """
        获取AI响应 - 支持Ollama和LM Studio

        Args:
            prompt: 完整的提示词
            model: 模型名称，如果为None则使用当前模型
            temperature: 温度参数

        Returns:
            AI响应文本
        """
        try:
            if model is None:
                model = self.state.current_model

            # 记录请求开始时间
            start_time = time.time()

            # 检测模型类型
            model_type = self.detect_model_type(model)

            if model_type == 'lm_studio':
                return self._get_lm_studio_response(prompt, model, temperature, start_time)
            elif model_type == 'ollama':
                return self._get_ollama_response(prompt, model, temperature, start_time)
            else:
                self.log_error(f"Unknown model type for model: {model}")
                return ""

        except Exception as e:
            self.log_error("Error getting AI response", e)
            return ""

    def _get_ollama_response(self, prompt: str, model: str, temperature: float, start_time: float) -> str:
        """获取Ollama响应"""
        try:
            request_data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "min_p": 0.05,
                    "top_k": 40,
                    "top_p": 0.9,
                    "num_ctx": 4096,
                    "repeat_penalty": 1.1
                }
            }

            response = requests.post(
                CONFIG["OLLAMA_URL"],
                json=request_data,
                timeout=CONFIG["REQUEST_TIMEOUT"]
            )
            response.raise_for_status()

            response_data = response.json()
            ai_response = response_data.get("response", "").strip()

            # 记录请求日志
            duration = time.time() - start_time
            self.log_ai_request(prompt, request_data, response_data, duration, {"provider": "ollama"})

            return ai_response

        except requests.exceptions.Timeout:
            self.log_error("Ollama request timed out")
            return ""
        except requests.exceptions.ConnectionError:
            self.log_error("Cannot connect to Ollama server")
            return ""

    def _get_lm_studio_response(self, prompt: str, model: str, temperature: float, start_time: float) -> str:
        """获取LM Studio响应（OpenAI格式）"""
        try:
            request_data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": DM_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": 2048,
                "stream": False
            }

            response = requests.post(
                CONFIG["LM_STUDIO_URL"],
                json=request_data,
                timeout=CONFIG["REQUEST_TIMEOUT"]
            )
            response.raise_for_status()

            response_data = response.json()
            ai_response = response_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

            # 记录请求日志
            duration = time.time() - start_time
            self.log_ai_request(prompt, request_data, response_data, duration, {"provider": "lm_studio"})

            return ai_response

        except requests.exceptions.Timeout:
            self.log_error("LM Studio request timed out")
            return ""
        except requests.exceptions.ConnectionError:
            self.log_error("Cannot connect to LM Studio server")
            return ""

    def speak(self, text: str, voice: str = "FemaleBritishAccent_WhyLucyWhy_Voice_2.wav") -> None:
        """
        文本转语音

        Args:
            text: 要转换的文本
            voice: 语音文件
        """
        try:
            if not text.strip():
                return

            if not self.check_alltalk_server():
                print("[TTS Server unavailable]")
                return

            payload = {
                "text_input": text,
                "character_voice_gen": voice,
                "narrator_enabled": "true",
                "narrator_voice_gen": "narrator.wav",
                "text_filtering": "none",
                "output_file_name": "output",
                "autoplay": "true",
                "autoplay_volume": "0.8"
            }

            response = requests.post(CONFIG["ALLTALK_API_URL"], data=payload, timeout=60)
            response.raise_for_status()

            # 这里可以添加音频播放逻辑
            # 由于依赖sounddevice，暂时只记录日志
            self.log_operation("tts_play", {"text_length": len(text), "voice": voice})

        except Exception as e:
            self.log_error("Error in TTS", e)

    def get_installed_models(self) -> List[str]:
        """获取已安装的模型列表（Ollama + LM Studio）"""
        models = []

        # 获取Ollama模型
        ollama_models = self.get_ollama_models()
        models.extend(ollama_models)

        # 获取LM Studio模型
        lm_studio_models = self.get_lm_studio_models()
        models.extend(lm_studio_models)

        return models

    def get_ollama_models(self) -> List[str]:
        """获取已安装的Ollama模型列表"""
        try:
            if not self.check_ollama_server():
                self.log_operation("ollama_server_unavailable", {"status": "Ollama server not running"})
                return []

            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                check=False,  # 改为False以处理非零退出状态
                timeout=30
            )

            # 检查命令是否成功
            if result.returncode != 0:
                self.log_error(f"Ollama list command failed with exit code {result.returncode}",
                              context={"stderr": result.stderr.strip()})
                return []

            models = []
            for line in result.stdout.strip().splitlines()[1:]:
                parts = line.split()
                if parts:
                    models.append(parts[0])
            return models

        except subprocess.TimeoutExpired:
            self.log_error("Ollama list command timed out")
            return []
        except Exception as e:
            self.log_error("Error getting Ollama models", e)
            return []

    def get_lm_studio_models(self) -> List[str]:
        """获取LM Studio可用模型列表"""
        try:
            if not self.check_lm_studio_server():
                return []

            response = requests.get("http://localhost:11435/v1/models", timeout=10)
            response.raise_for_status()

            data = response.json()
            models = []
            for model in data.get("data", []):
                model_id = model.get("id", "")
                if model_id:
                    models.append(model_id)
            return models

        except requests.exceptions.Timeout:
            self.log_error("LM Studio models request timed out")
            return []
        except requests.exceptions.ConnectionError:
            self.log_error("Cannot connect to LM Studio server")
            return []
        except Exception as e:
            self.log_error("Error getting LM Studio models", e)
            return []

    def setup_directories(self) -> None:
        """确保必要的目录存在"""
        os.makedirs("logs", exist_ok=True)
        os.makedirs("saves", exist_ok=True)