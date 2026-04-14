"""ReAct 循环逻辑模块

实现基于 ReAct (Reasoning and Acting) 范式的核心循环：
- Thought: 思考下一步行动
- Action: 执行工具调用
- Observation: 观察工具返回结果
- Loop: 循环直到任务完成
"""

import json
import logging
from enum import Enum
from typing import Any, Optional, Callable
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class AgentState(str, Enum):
    """ReAct 循环状态"""
    THINKING = "THINKING"
    ACTION = "ACTION"
    OBSERVING = "OBSERVING"
    FINISH = "FINISH"
    ERROR = "ERROR"


@dataclass
class ActionResult:
    """行动结果"""
    success: bool
    content: Any
    error: Optional[str] = None


@dataclass
class ReActContext:
    """ReAct 循环上下文"""
    task: str
    history: list[dict] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    current_state: AgentState = AgentState.THINKING
    iteration: int = 0
    result: Any = None


class ReActLoop:
    """ReAct 循环执行器"""

    def __init__(
        self,
        llm_client: Any,
        tool_registry: dict[str, Callable],
        max_iterations: int = 50
    ):
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        self.max_iterations = max_iterations

    def run(self, task: str, system_prompt: str) -> tuple[str, list[dict]]:
        """运行 ReAct 循环

        Args:
            task: 用户任务
            system_prompt: 系统提示词

        Returns:
            (最终结果, 循环历史)
        """
        context = ReActContext(task=task)
        self.llm_client.clear_history()
        self.llm_client.add_system_message(system_prompt)

        while context.current_state != AgentState.FINISH:
            if context.iteration >= self.max_iterations:
                logger.warning(f"达到最大迭代次数 {self.max_iterations}")
                context.current_state = AgentState.ERROR
                context.result = "达到最大迭代次数，任务未能完成"
                break

            try:
                if context.current_state == AgentState.THINKING:
                    self._handle_thinking(context)
                elif context.current_state == AgentState.ACTION:
                    self._handle_action(context)
                elif context.current_state == AgentState.OBSERVING:
                    self._handle_observing(context)
            except Exception as e:
                logger.error(f"ReAct 循环出错: {e}")
                context.current_state = AgentState.ERROR
                context.result = f"执行出错: {str(e)}"
                break

            context.iteration += 1

        return context.result, context.history

    def _handle_thinking(self, context: ReActContext) -> None:
        """处理思考状态"""
        user_message = self._build_thinking_prompt(context)
        raw_response = self.llm_client.call_with_tools(user_message)
        response = self.llm_client.parse_response(raw_response)
        self.llm_client.add_llm_response(raw_response)

        text = response.get("content") or ""
        has_tools = response.get("has_tool_calls", False)

        if has_tools and response.get("tool_calls"):
            tool_calls = response["tool_calls"]
            first_tool = tool_calls[0]

            context.history.append({
                "state": "THINKING",
                "thought": text,
                "action": {"tool": first_tool["name"], "args": first_tool["input"]}
            })
            context.current_state = AgentState.ACTION
            context._pending_tool_calls = tool_calls

        elif response.get("stop_reason") == "end_turn" or (text and "FINISH" in text.upper()):
            context.current_state = AgentState.FINISH
            context.result = text
            context.history.append({
                "state": "THINKING",
                "thought": text,
                "action": "FINISH"
            })
        else:
            if text.strip():
                context.observations.append(text)
            context.current_state = AgentState.THINKING

    def _handle_action(self, context: ReActContext) -> None:
        """处理行动状态"""
        pending_calls = getattr(context, "_pending_tool_calls", [])
        if not pending_calls:
            context.current_state = AgentState.ERROR
            return

        all_results = []
        for tool_call in pending_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["input"]
            tool_use_id = tool_call["id"]

            tool_func = self.tool_registry.get(tool_name)

            if not tool_func:
                result_content = json.dumps({"error": f"未知工具: {tool_name}"})
            else:
                try:
                    args = tool_args if isinstance(tool_args, dict) else json.loads(tool_args)
                    tool_output = tool_func(**args)
                    result_content = json.dumps(tool_output) if tool_output else "null"
                except Exception as e:
                    result_content = json.dumps({"error": str(e)})

            self.llm_client.add_tool_result(tool_use_id, result_content)
            all_results.append(result_content)

        context.history.append({
            "state": "ACTION",
            "tool": pending_calls[0]["name"],
            "args": pending_calls[0]["input"],
            "result": all_results[0] if all_results else None
        })

        combined_result = "\n".join([
            f"工具 {tc['name']} 的结果: {r}" 
            for tc, r in zip(pending_calls, all_results)
        ])
        context.observations.append(combined_result)
        context.current_state = AgentState.OBSERVING

    def _handle_observing(self, context: ReActContext) -> None:
        """处理观察状态"""
        last_obs = context.observations[-1] if context.observations else ""
        context.history.append({
            "state": "OBSERVING",
            "observation": last_obs[:200] + "..." if len(last_obs) > 200 else last_obs
        })
        context.current_state = AgentState.THINKING

    def _build_thinking_prompt(self, context: ReActContext) -> str:
        """构建思考 Prompt"""
        parts = [f"任务: {context.task}\n"]

        if context.observations:
            parts.append("【最近观察结果】")
            for obs in context.observations[-3:]:
                parts.append(f"- {obs[:500]}")
            parts.append("")

        parts.append("请根据任务和观察结果，决定下一步行动。如果需要写作，请直接输出小说内容；如果需要查询信息，请说明要查询什么。")

        return "\n".join(parts)


class ToolRegistry:
    """工具注册表"""

    def __init__(self):
        self._tools: dict[str, Callable] = {}

    def register(self, name: str, func: Callable) -> None:
        """注册工具"""
        self._tools[name] = func

    def get(self, name: str) -> Optional[Callable]:
        """获取工具"""
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """列出所有工具"""
        return list(self._tools.keys())

    def get_definitions(self) -> list[dict]:
        """获取工具定义列表（用于 API）"""
        return [
            {
                "name": name,
                "description": func.__doc__ or "",
                "input_schema": {"type": "object", "properties": {}}
            }
            for name, func in self._tools.items()
        ]
