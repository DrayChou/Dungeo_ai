#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共享日志系统模块
提供完整的日志功能，支持操作记录、AI请求记录、游戏行为记录和错误记录
"""

import datetime
import time
import json
import traceback
import os
from typing import Dict, List, Optional, Any


class GameLogger:
    """统一的游戏日志系统"""

    def __init__(self, log_file_path: str = "error_log.txt"):
        """
        初始化日志系统

        Args:
            log_file_path: 基础日志文件路径，其他日志文件将基于此路径生成
        """
        self.base_log_path = log_file_path
        self.base_dir = os.path.dirname(log_file_path)
        if not self.base_dir:
            self.base_dir = "."

        # 确保日志目录存在
        os.makedirs(os.path.join(self.base_dir, "logs"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "saves"), exist_ok=True)

        # 设置各类型日志文件的完整路径
        self.error_log_path = log_file_path
        self.operation_log_path = os.path.join(self.base_dir, "logs", "operation_log.txt")
        self.ai_log_path = os.path.join(self.base_dir, "logs", "ai_log.txt")
        self.game_log_path = os.path.join(self.base_dir, "logs", "game_log.txt")

    def log_error(self, error_message: str, exception: Optional[Exception] = None,
                  context: Optional[Dict[str, Any]] = None) -> None:
        """
        增强的错误日志记录

        Args:
            error_message: 错误消息
            exception: 异常对象
            context: 额外的上下文信息
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(self.error_log_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"\n--- ERROR [{timestamp}] ---\n")
                log_file.write(f"Message: {error_message}\n")

                if exception:
                    log_file.write(f"Exception: {type(exception).__name__}: {str(exception)}\n")
                    traceback.print_exc(file=log_file)

                if context:
                    log_file.write("Context:\n")
                    for key, value in context.items():
                        log_file.write(f"  {key}: {value}\n")

                log_file.write("--- END ERROR ---\n")

        except Exception as e:
            print(f"CRITICAL: Failed to write to error log: {e}")

    def log_operation(self, operation: str, parameters: dict = None, result: str = None,
                      duration: float = None, context: Optional[Dict[str, Any]] = None) -> None:
        """
        记录操作日志

        Args:
            operation: 操作名称
            parameters: 操作参数
            result: 操作结果
            duration: 操作持续时间（秒）
            context: 游戏上下文信息
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            with open(self.operation_log_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"\n=== OPERATION [{timestamp}] ===\n")
                log_file.write(f"Operation: {operation}\n")

                if parameters:
                    log_file.write("Parameters:\n")
                    for key, value in parameters.items():
                        if isinstance(value, str) and len(value) > 200:
                            value = value[:200] + "..." + (f" (truncated, total: {len(value)} chars)" if len(value) > 200 else "")
                        log_file.write(f"  {key}: {value}\n")

                if result:
                    result_log = result[:500] + "..." if len(result) > 500 else result
                    log_file.write(f"Result: {result_log}\n")

                if duration is not None:
                    log_file.write(f"Duration: {duration:.3f}s\n")

                if context:
                    log_file.write("Context:\n")
                    for key, value in context.items():
                        log_file.write(f"  {key}: {value}\n")

                log_file.write("=== END OPERATION ===\n")

        except Exception as e:
            print(f"CRITICAL: Failed to write operation log: {e}")

    def log_ai_request(self, prompt: str, request_data: dict, response_data: dict,
                       duration: float, context: Optional[Dict[str, Any]] = None) -> None:
        """
        详细的AI请求日志记录 - 完整无截断内容

        Args:
            prompt: 完整的AI提示
            request_data: 请求数据
            response_data: 响应数据
            duration: 请求持续时间
            context: 游戏上下文信息
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            with open(self.ai_log_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"\n🤖 AI REQUEST [{timestamp}] 🤖\n")

                if context:
                    model = context.get("model", "unknown")
                    log_file.write(f"Model: {model}\n")

                log_file.write(f"Duration: {duration:.3f}s\n")
                log_file.write(f"Prompt Length: {len(prompt)} characters\n")

                # 记录完整的请求参数
                log_file.write("Request Parameters:\n")
                for key, value in request_data.items():
                    if key == "prompt":
                        log_file.write(f"  {key}: [COMPLETE PROMPT - Length: {len(str(value))} chars]\n")
                        log_file.write("  " + "="*80 + "\n")
                        log_file.write(f"  {str(value)}\n")
                        log_file.write("  " + "="*80 + "\n")
                    elif key == "options":
                        log_file.write(f"  {key}:\n")
                        for opt_key, opt_value in value.items():
                            log_file.write(f"    {opt_key}: {opt_value}\n")
                    else:
                        log_file.write(f"  {key}: {value}\n")

                # 记录完整的响应详情
                if response_data:
                    log_file.write("Response Details:\n")
                    for key, value in response_data.items():
                        if key == "response":
                            log_file.write(f"  {key}: [COMPLETE RESPONSE - Length: {len(str(value))} chars]\n")
                            log_file.write("  " + "="*80 + "\n")
                            log_file.write(f"  {str(value)}\n")
                            log_file.write("  " + "="*80 + "\n")
                        elif key == "thinking":
                            log_file.write(f"  {key}: [COMPLETE THINKING - Length: {len(str(value))} chars]\n")
                            log_file.write("  " + "="*80 + "\n")
                            log_file.write(f"  {str(value)}\n")
                            log_file.write("  " + "="*80 + "\n")
                        elif key == "context":
                            log_file.write(f"  {key}: [Array length: {len(value) if isinstance(value, list) else 'N/A'}]\n")
                            log_file.write(f"    First 20 tokens: {value[:20] if isinstance(value, list) else 'N/A'}\n")
                        elif key in ["created_at", "total_duration", "load_duration", "prompt_eval_duration", "eval_duration"]:
                            log_file.write(f"  {key}: {value}\n")
                        else:
                            log_file.write(f"  {key}: {str(value)}\n")

                # 记录游戏上下文
                if context:
                    log_file.write("Game Context:\n")
                    for key, value in context.items():
                        log_file.write(f"  {key}: {value}\n")

                log_file.write("🤖 END AI REQUEST 🤖\n")

        except Exception as e:
            print(f"CRITICAL: Failed to write AI log: {e}")

    def log_game_action(self, action: str, details: dict = None,
                       conversation: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> None:
        """
        记录游戏行为和玩家交互 - 完整无截断内容

        Args:
            action: 行为名称
            details: 行为详情
            conversation: 完整对话内容
            context: 游戏状态上下文
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            with open(self.game_log_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"\n🎮 GAME ACTION [{timestamp}] 🎮\n")
                log_file.write(f"Action: {action}\n")

                if details:
                    log_file.write("Details:\n")
                    for key, value in details.items():
                        log_file.write(f"  {key}: {value}\n")

                if context:
                    log_file.write("Current State:\n")
                    for key, value in context.items():
                        log_file.write(f"  {key}: {value}\n")

                # 对于重要行为，记录完整对话状态
                if action in ["player_input", "ai_response_received", "conversation_updated"] and conversation:
                    log_file.write("Complete Conversation:\n")
                    log_file.write("  " + "="*80 + "\n")
                    log_file.write(f"  {conversation}\n")
                    log_file.write("  " + "="*80 + "\n")

                log_file.write("🎮 END GAME ACTION 🎮\n")

        except Exception as e:
            print(f"CRITICAL: Failed to write game log: {e}")

    @staticmethod
    def create_default_logger(base_path: str = "error_log.txt") -> 'GameLogger':
        """
        创建默认的日志器实例

        Args:
            base_path: 基础日志文件路径

        Returns:
            GameLogger: 日志器实例
        """
        return GameLogger(base_path)