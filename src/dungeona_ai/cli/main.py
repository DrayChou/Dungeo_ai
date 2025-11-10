#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Dungeon Master Adventure - 命令行版本
使用共享游戏核心模块的重构版本
"""

import random
import time
import json
import traceback
import threading
import os
from typing import Dict, List, Optional, Tuple

# Import shared game core
from ..core import (
    GameCore, GameState, CONFIG, DM_SYSTEM_PROMPT,
    get_genre_description, get_role_starter,
    ROLE_STARTERS, t, get_current_language
)


class AdventureGame:
    """AdventureGame class using shared GameCore"""

    def __init__(self):
        self.core = GameCore(CONFIG["LOG_FILE"])
        self.state = self.core.state
        self._setup_directories()

    def _setup_directories(self):
        """Ensure necessary directories exist"""
        self.core.setup_directories()

    def log_error(self, error_message: str, exception: Optional[Exception] = None) -> None:
        """Enhanced error logging"""
        self.core.log_error(error_message, exception, {
            "interface": "cli",
            "model": self.state.current_model,
            "character_name": self.state.character_name
        })

    def select_model(self) -> str:
        """Interactive model selection with fallback"""
        models = self.core.get_installed_models()

        if not models:
            print(t("ui.no_models_found"))
            model_input = input(t("ui.enter_model_name").format(default_model=CONFIG["DEFAULT_MODEL"]))
            return model_input or CONFIG["DEFAULT_MODEL"]

        print("\n" + t("ui.available_models"))
        for idx, model in enumerate(models, 1):
            # 显示模型类型标识
            if '/' in model:
                model_type = "[LM Studio]"
            elif ':' in model:
                model_type = "[Ollama]"
            else:
                model_type = "[Unknown]"
            print(f"  {idx}: {model} {model_type}")

        while True:
            try:
                choice = input(t("ui.select_model").format(count=len(models), default_model=CONFIG["DEFAULT_MODEL"]))

                if not choice:
                    return CONFIG["DEFAULT_MODEL"]

                idx = int(choice) - 1
                if 0 <= idx < len(models):
                    return models[idx]
                else:
                    print(t("ui.please_enter_number").format(count=len(models)))

            except ValueError:
                print(t("ui.please_enter_valid_number"))
            except KeyboardInterrupt:
                print("\n" + t("ui.using_default_model"))
                return CONFIG["DEFAULT_MODEL"]

    def select_genre_and_role(self) -> Tuple[str, str]:
        """Interactive genre and role selection"""
        genres = {
            "1": "Fantasy", "2": "Sci-Fi", "3": "Cyberpunk",
            "4": "Post-Apocalyptic", "5": "1880", "6": "WW1",
            "7": "1925 New York", "8": "Roman Empire", "9": "French Revolution"
        }

        print(t("ui.choose_genre"))
        for key, name in genres.items():
            print(f"{key}: {name}")

        while True:
            genre_choice = input(t("ui.enter_choice_number"))
            selected_genre = genres.get(genre_choice)
            if selected_genre:
                break
            print(t("ui.invalid_choice_try_again"))

        # Show genre description
        print(f"\n{selected_genre}: {get_genre_description(selected_genre)}\n")

        # Role selection
        roles = list(ROLE_STARTERS[selected_genre].keys())
        print(t("ui.choose_role_in_genre").format(genre=selected_genre))
        for idx, role in enumerate(roles, 1):
            print(f"{idx}: {role}")

        while True:
            role_choice = input(t("ui.enter_role_choice_or_random")).strip().lower()
            if role_choice == 'r':
                selected_role = random.choice(roles)
                break
            try:
                idx = int(role_choice) - 1
                if 0 <= idx < len(roles):
                    selected_role = roles[idx]
                    break
            except ValueError:
                pass
            print(t("ui.invalid_choice_try_again"))

        return selected_genre, selected_role

    def start_new_adventure(self) -> bool:
        """Start a new adventure with character creation"""
        try:
            self.state.selected_genre, self.state.selected_role = self.select_genre_and_role()

            self.state.character_name = input(t("ui.enter_character_name")) or t("defaults.character_name")

            starter = get_role_starter(self.state.selected_genre, self.state.selected_role)

            print(f"\n" + t("ui.adventure_start").format(name=self.state.character_name, role=self.state.selected_role))
            print(t("ui.starting_scenario").format(scenario=starter))
            print(t("ui.type_help_for_commands") + "\n")

            # Initial setup
            initial_context = (
                f"### Adventure Setting ###\n"
                f"Genre: {self.state.selected_genre}\n"
                f"Player Character: {self.state.character_name} the {self.state.selected_role}\n"
                f"Starting Scenario: {starter}\n\n"
                "Dungeon Master: "
            )

            self.state.conversation = initial_context

            # Get first response
            full_prompt = DM_SYSTEM_PROMPT + "\n\n" + self.state.conversation
            ai_reply = self.core.get_ai_response(full_prompt)
            if ai_reply:
                print(t("ui.dungeon_master").format(response=ai_reply))
                self.core.speak(ai_reply)
                self.state.conversation += ai_reply
                self.state.last_ai_reply = ai_reply
                self.state.adventure_started = True
                return True
            else:
                print(t("ui.failed_to_get_initial_response"))
                return False

        except Exception as e:
            self.log_error(t("ui.error_starting_adventure").format(error=e), e)
            return False

    def show_help(self) -> None:
        """Display available commands"""
        print(t("ui.available_commands"))

    def show_status(self) -> None:
        """Display current game status"""
        print(f"\n{t('ui.current_game_status')}")
        print(t("ui.character").format(name=self.state.character_name, role=self.state.selected_role))
        print(t("ui.genre").format(genre=self.state.selected_genre))
        print(t("ui.model").format(model=self.state.current_model))
        print(t("ui.adventure_started").format(status=t("ui.started") if self.state.adventure_started else t("ui.not_started")))
        if self.state.last_ai_reply:
            print(t("ui.last_action").format(action=self.state.last_player_input[:50] + "..."))
        print(t("ui.status_separator"))

    def save_adventure(self) -> bool:
        """Save adventure to file with error handling"""
        try:
            save_data = {
                "conversation": self.state.conversation,
                "metadata": {
                    "character_name": self.state.character_name,
                    "genre": self.state.selected_genre,
                    "role": self.state.selected_role,
                    "model": self.state.current_model,
                    "save_time": datetime.datetime.now().isoformat()
                }
            }

            with open(CONFIG["SAVE_FILE"], "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            print(t("ui.adventure_saved_successfully"))
            return True

        except Exception as e:
            self.log_error(t("ui.failed_to_save_adventure"), e)
            print(t("ui.failed_to_save_adventure"))
            return False

    def load_adventure(self) -> bool:
        """Load adventure from file with error handling"""
        try:
            if not os.path.exists(CONFIG["SAVE_FILE"]):
                print(t("ui.no_saved_adventure_found"))
                return False

            with open(CONFIG["SAVE_FILE"], "r", encoding="utf-8") as f:
                save_data = json.load(f)

            self.state.conversation = save_data["conversation"]
            metadata = save_data.get("metadata", {})

            self.state.character_name = metadata.get("character_name", t("defaults.character_name"))
            self.state.selected_genre = metadata.get("genre", "Fantasy")
            self.state.selected_role = metadata.get("role", "Adventurer")
            self.state.current_model = metadata.get("model", CONFIG["DEFAULT_MODEL"])

            # Extract last AI reply
            last_dm = self.state.conversation.rfind("Dungeon Master:")
            if last_dm != -1:
                self.state.last_ai_reply = self.state.conversation[last_dm + len("Dungeon Master:"):].strip()

            self.state.adventure_started = True
            print(t("ui.adventure_loaded_successfully"))
            return True

        except Exception as e:
            self.log_error(t("ui.failed_to_load_adventure"), e)
            print(t("ui.failed_to_load_adventure"))
            return False

    def process_command(self, command: str) -> bool:
        """Process game commands"""
        cmd = command.lower().strip()

        if cmd in ["/?", "/help"]:
            self.show_help()
        elif cmd == "/exit":
            print(t("ui.exiting_adventure"))
            return False
        elif cmd == "/save":
            self.save_adventure()
        elif cmd == "/load":
            self.load_adventure()
        elif cmd == "/status":
            self.show_status()
        else:
            print(t("ui.unknown_command").format(command=command))

        return True

    def process_player_input(self, user_input: str) -> None:
        """Process regular player input"""
        self.state.last_player_input = user_input
        formatted_input = f"Player: {user_input}"

        prompt = (
            f"{DM_SYSTEM_PROMPT}\n\n"
            f"{self.state.conversation}\n"
            f"{formatted_input}\n"
            "Dungeon Master:"
        )

        ai_reply = self.core.get_ai_response(prompt)
        if ai_reply:
            print(f"\n{t('ui.dungeon_master').format(response=ai_reply)}")
            self.core.speak(ai_reply)
            self.state.conversation += f"\n{formatted_input}\nDungeon Master: {ai_reply}"
            self.state.last_ai_reply = ai_reply
        else:
            print(t("ui.failed_to_get_response_try_again"))

    def run(self) -> None:
        """Main game loop"""
        print(t("ui.game_title") + "\n")

        # Model selection
        self.state.current_model = self.select_model()
        print(t("ui.using_model").format(model=self.state.current_model) + "\n")

        # Load or start adventure
        if os.path.exists(CONFIG["SAVE_FILE"]):
            print(t("ui.saved_adventure_exists"))
            if input().strip().lower() == 'y':
                if self.load_adventure():
                    print(f"\n{t('ui.dungeon_master').format(response=self.state.last_ai_reply)}")
                    self.core.speak(self.state.last_ai_reply)

        if not self.state.adventure_started:
            if not self.start_new_adventure():
                return

        # Main game loop
        while self.state.adventure_started:
            try:
                user_input = input(t("ui.prompt")).strip()
                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith('/'):
                    if not self.process_command(user_input):
                        break
                else:
                    self.process_player_input(user_input)

            except KeyboardInterrupt:
                print("\n" + t("ui.game_interrupted"))
            except Exception as e:
                self.log_error(t("ui.unexpected_error"), e)
                print(t("ui.unexpected_error"))


def main():
    """Main entry point with exception handling"""
    try:
        game = AdventureGame()
        game.run()
    except Exception as e:
        print(t("ui.fatal_error").format(error=e))
        print(t("ui.check_error_log"))


if __name__ == "__main__":
    main()