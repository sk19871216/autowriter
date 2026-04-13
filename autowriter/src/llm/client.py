"""LLMClient - MiniMax Anthropic API 封装模块

完全按照官方文档使用 Anthropic SDK：
- base_url: https://api.minimaxi.com/anthropic
- SDK 自动处理 /messages 拼接
- SDK 自动处理消息格式
"""

import os
from typing import Optional, Dict, Any
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

    def _get_client(self) -> anthropic.Anthropic:
        """获取 Anthropic 客户端"""
        if self._client is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("MINIMAX_START")
            self._client = anthropic.Anthropic(
                api_key=api_key,
                base_url="https://api.minimaxi.com/anthropic"
            )
        return self._client

    def create_message(
        self,
        system: str,
        user_message: str,
        max_tokens: int = 4000
    ):
        """发送消息并获取响应（完全按照官方文档）"""
        client = self._get_client()
        
        message = client.messages.create(
            model="MiniMax-M2.7",
            max_tokens=max_tokens,
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_message
                        }
                    ]
                }
            ]
        )
        
        return message

    def set_tools(self, tools: list) -> None:
        """设置工具（兼容旧接口）"""
        self._tools = tools

    def clear_history(self) -> None:
        """清空消息历史"""
        self._messages = []

    def add_system_message(self, content: str) -> None:
        """设置系统消息"""
        self._system_message = content

    def call_with_tools(self, user_message: str, system_message: str = None, max_tokens: int = 4000):
        """调用 API（支持工具调用）- 当前简化为普通调用"""
        return self.create_message(
            system=system_message or self._system_message,
            user_message=user_message,
            max_tokens=max_tokens
        )

    def call(
        self,
        prompt: str,
        system: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Any:
        """发送消息并获取响应的便捷方法

        Args:
            prompt: 用户消息
            system: 系统消息
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            消息对象
        """
        response = self.create_message(
            system=system or self._system_message,
            user_message=prompt,
            max_tokens=max_tokens
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
        
        return result


def create_llm_client() -> LLMClient:
    """工厂函数：创建 LLM 客户端"""
    return LLMClient()
