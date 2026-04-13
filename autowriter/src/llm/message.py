"""消息格式处理模块 - Anthropic 兼容格式"""

from typing import Any, Optional, Literal, Union
from pydantic import BaseModel, Field


class TextContent(BaseModel):
    """文本内容块"""
    type: Literal["text"] = "text"
    text: str


class ToolUse(BaseModel):
    """工具调用块"""
    type: Literal["tool_use"] = "tool_use"
    id: str
    name: str
    input: dict


class ToolResult(BaseModel):
    """工具结果块"""
    type: Literal["tool_result"] = "tool_result"
    tool_use_id: str
    content: str


ContentBlock = Union[TextContent, ToolUse, ToolResult]


class Message(BaseModel):
    """对话消息 - Anthropic 格式"""
    role: Literal["system", "user", "assistant"]
    content: Union[str, list[ContentBlock]] = ""

    def to_dict(self) -> dict:
        """转换为字典格式"""
        if isinstance(self.content, str):
            return {"role": self.role, "content": self.content}
        return {"role": self.role, "content": [c.model_dump() for c in self.content]}


class ToolDefinition(BaseModel):
    """工具定义 - Anthropic 格式"""
    name: str
    description: str
    input_schema: dict

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }


class ToolCall(BaseModel):
    """工具调用"""
    id: str
    type: str = "tool_use"
    name: str
    input: dict


class LLMResponse(BaseModel):
    """LLM 响应"""
    content: Optional[str] = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    thinking: Optional[str] = None
    finish_reason: Optional[str] = None
    usage: dict = Field(default_factory=dict)

    def has_tool_calls(self) -> bool:
        """是否有工具调用"""
        return len(self.tool_calls) > 0

    def get_first_action(self) -> Optional[tuple[str, dict]]:
        """获取第一个工具调用 (name, input)"""
        if self.tool_calls:
            tc = self.tool_calls[0]
            return (tc.name, tc.input)
        return None


class MessageHistory:
    """消息历史管理器 - Anthropic 格式"""

    def __init__(self, max_messages: int = 100):
        self.messages: list[Message] = []
        self.max_messages = max_messages
        self._tool_use_id_counter = 0

    def new_tool_use_id(self) -> str:
        """生成新的 tool_use_id"""
        self._tool_use_id_counter += 1
        return f"tool_{self._tool_use_id_counter}"

    def add_system(self, content: str) -> None:
        """添加系统消息"""
        self.messages.append(Message(role="system", content=content))

    def add_user(self, content: str) -> None:
        """添加用户消息"""
        self.messages.append(Message(
            role="user",
            content=[{"type": "text", "text": content}]
        ))

    def add_assistant(self, content: Any) -> None:
        """添加助手消息"""
        if isinstance(content, str):
            self.messages.append(Message(
                role="assistant",
                content=[{"type": "text", "text": content}]
            ))
        else:
            self.messages.append(Message(role="assistant", content=content))

    def add_tool_result(self, tool_use_id: str, content: str) -> None:
        """添加工具结果消息"""
        self.messages.append(Message(
            role="user",
            content=[{
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": content
            }]
        ))

    def get_messages(self) -> list[dict]:
        """获取所有消息的字典列表"""
        return [msg.to_dict() for msg in self.messages]

    def get_recent(self, count: int) -> list[dict]:
        """获取最近 N 条消息"""
        return [msg.to_dict() for msg in self.messages[-count:]]

    def clear(self) -> None:
        """清空历史"""
        self.messages.clear()
        self._tool_use_id_counter = 0

    def __len__(self) -> int:
        return len(self.messages)
