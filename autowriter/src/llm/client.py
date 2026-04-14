"""LLMClient - MiniMax Anthropic API 封装模块

完全按照官方文档使用 Anthropic SDK：
- base_url: https://api.minimaxi.com/anthropic
- SDK 自动处理 /messages 拼接
- SDK 自动处理消息格式
"""

import os
import re
import json
from typing import Optional, Dict, Any, List
import anthropic

from autowriter.config.settings import DEFAULT_CONFIG


class LLMConfig:
    """LLM 配置"""
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("MINIMAX_START", "")


class LLMClient:
    """MiniMax Anthropic API 客户端（官方 SDK）"""

    def __init__(self):
        self._client: Optional[anthropic.Anthropic] = None
        self._messages = []
        self._tools = []
        self._system_message = ""
        self.config = LLMConfig()
        self._tool_call_counter = 0
        self._pending_tool_results: List[Dict] = []

    def _get_client(self) -> anthropic.Anthropic:
        """获取 Anthropic 客户端"""
        if self._client is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("MINIMAX_START")
            self._client = anthropic.Anthropic(
                api_key=api_key,
                base_url="https://api.minimaxi.com/anthropic"
            )
        return self._client

    def add_tool_result(self, tool_use_id: str, content: str) -> None:
        """添加工具结果到缓冲区（不立即发送）"""
        self._pending_tool_results.append({
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": content
        })

    def flush_tool_results(self) -> None:
        """将缓冲的工具结果作为单个 user 消息发送"""
        if self._pending_tool_results:
            self._messages.append({
                "role": "user",
                "content": self._pending_tool_results
            })
            self._pending_tool_results = []

    def add_llm_response(self, message) -> None:
        """保存 LLM 的回复到消息历史"""
        assistant_content = []
        has_tool_use = False
        text_content = ""

        for block in message.content:
            if block.type == "text":
                text_content += block.text
                assistant_content.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                has_tool_use = True
                assistant_content.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })

        if has_tool_use and assistant_content:
            self._messages.append({
                "role": "assistant",
                "content": assistant_content
            })
        elif text_content:
            self._messages.append({
                "role": "assistant",
                "content": [{"type": "text", "text": text_content}]
            })

    def _build_messages(self, user_message: str) -> List[Dict]:
        """构建消息列表"""
        self.flush_tool_results()
        messages = list(self._messages)
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_message
                }
            ]
        })
        return messages

    def clear_conversation(self) -> None:
        """清除对话历史（保留系统消息）"""
        self._messages = []
        self._pending_tool_results = []

    def create_message(
        self,
        system: str,
        user_message: str,
        max_tokens: int = 4000,
        tools: List[Dict] = None
    ):
        """发送消息并获取响应"""
        client = self._get_client()
        messages = self._build_messages(user_message)

        import logging
        logging.info(f"[DEBUG] 发送消息数量: {len(messages)}")
        for i, msg in enumerate(messages):
            logging.info(f"[DEBUG] 消息 {i}: role={msg['role']}")
            for block in msg.get("content", []):
                logging.info(f"[DEBUG]   block type: {block.get('type')}")
                if block.get("type") == "tool_use":
                    logging.info(f"[DEBUG]     id: {block.get('id')}, name: {block.get('name')}")
                elif block.get("type") == "tool_result":
                    logging.info(f"[DEBUG]     tool_use_id: {block.get('tool_use_id')}")

        if tools:
            message = client.messages.create(
                model="MiniMax-M2.7",
                max_tokens=max_tokens,
                system=system,
                messages=messages,
                tools=tools
            )
        else:
            message = client.messages.create(
                model="MiniMax-M2.7",
                max_tokens=max_tokens,
                system=system,
                messages=messages
            )

        return message

    def set_tools(self, tools: list) -> None:
        """设置工具（兼容旧接口）"""
        self._tools = tools

    def clear_history(self) -> None:
        """清空消息历史"""
        self._messages = []
        self._pending_tool_results = []

    def add_system_message(self, content: str) -> None:
        """设置系统消息"""
        self._system_message = content

    def call_with_tools(self, user_message: str, system_message: str = None, max_tokens: int = 4000):
        """调用 API（支持工具调用）"""
        return self.create_message(
            system=system_message or self._system_message,
            user_message=user_message,
            max_tokens=max_tokens,
            tools=self._tools if self._tools else None
        )

    def call(
        self,
        prompt: str,
        system: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Any:
        """发送消息并获取响应的便捷方法（不使用工具，纯文本生成）

        Args:
            prompt: 用户消息
            system: 系统消息
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            消息对象
        """
        self.flush_tool_results()
        client = self._get_client()
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
        
        response = client.messages.create(
            model="MiniMax-M2.7",
            max_tokens=max_tokens,
            system=system or self._system_message,
            messages=messages
        )
        return response

    def parse_response(self, message) -> dict:
        """解析响应（按照官方文档）"""
        result = {
            "content": "",
            "tool_calls": [],
            "stop_reason": message.stop_reason,
            "has_tool_calls": False
        }
        
        for block in message.content:
            if block.type == "text":
                result["content"] += block.text
            elif block.type == "tool_use":
                result["tool_calls"].append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })
                result["has_tool_calls"] = True
            elif block.type == "tool_result":
                self.add_tool_result(block.tool_use_id, block.content)
            elif block.type == "thinking":
                pass

        return result


def create_llm_client() -> LLMClient:
    """工厂函数：创建 LLM 客户端"""
    return LLMClient()
