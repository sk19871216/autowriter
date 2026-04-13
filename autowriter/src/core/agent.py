"""WritingAgent - 小说写作智能体核心

基于 ReAct 范式的写作智能体，是系统的"大脑"：
- 负责任思考和决策
- 调用工具执行具体任务
- 维护写作上下文
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field

from autowriter.config.settings import DEFAULT_CONFIG, SystemConfig
from autowriter.src.llm.client import LLMClient
from autowriter.src.llm.message import ToolDefinition
from autowriter.src.core.react import ReActLoop, ToolRegistry, AgentState
from autowriter.src.core.state import SessionState
from autowriter.src.memory import MemoryRetriever, MemoryIntegrator


logger = logging.getLogger(__name__)


@dataclass
class WritingTask:
    """写作任务"""
    task_type: str
    content: str
    chapter: Optional[int] = None
    context: dict = field(default_factory=dict)


@dataclass
class WritingResult:
    """写作结果"""
    success: bool
    content: Any
    task_type: str
    history: list[dict] = field(default_factory=list)
    error: Optional[str] = None


class WritingAgent:
    """小说写作智能体

    基于 ReAct 范式实现思考-行动-观察的循环决策。
    通过调用工具完成写作任务。
    """

    def __init__(
        self,
        project_path: str = "my_novel",
        config: Optional[SystemConfig] = None
    ):
        self.config = config or DEFAULT_CONFIG
        self.project_path = Path(project_path)
        self.session_state = SessionState(session_id="", project_path=str(self.project_path))

        self.tool_registry = ToolRegistry()
        self.llm_client = LLMClient()
        self._setup_tools()

        self.memory_retriever = MemoryRetriever(str(self.project_path))
        self.memory_integrator = MemoryIntegrator(str(self.project_path))

        self.react_loop = ReActLoop(
            llm_client=self.llm_client,
            tool_registry=self.tool_registry,
            max_iterations=self.config.react.max_iterations
        )

    def _setup_tools(self) -> None:
        """设置可用工具"""
        self.tool_registry.register("query_memory", self._tool_query_memory)
        self.tool_registry.register("write_draft", self._tool_write_draft)
        self.tool_registry.register("revise_draft", self._tool_revise_draft)

        tool_defs = [
            ToolDefinition(
                name="query_memory",
                description="查询角色、世界观或任何故事背景信息。"
                            "当需要了解角色外貌、性格、过往，或需要了解地点设定、"
                            "世界观规则时使用。",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "查询内容，可以是角色名、地点名或关键词"
                        }
                    },
                    "required": ["query"]
                }
            ),
            ToolDefinition(
                name="write_draft",
                description="根据给定的大纲和上下文，创作新的章节文本。"
                            "当你有足够的背景信息，可以开始写作时使用。",
                input_schema={
                    "type": "object",
                    "properties": {
                        "chapter": {
                            "type": "integer",
                            "description": "章节号"
                        },
                        "outline": {
                            "type": "string",
                            "description": "章节大纲"
                        }
                    },
                    "required": ["chapter", "outline"]
                }
            ),
            ToolDefinition(
                name="revise_draft",
                description="根据修改指令，修改已有的章节文本。"
                            "当需要调整已有内容、修正错误或改进文风时使用。",
                input_schema={
                    "type": "object",
                    "properties": {
                        "chapter": {
                            "type": "integer",
                            "description": "章节号"
                        },
                        "instruction": {
                            "type": "string",
                            "description": "修改指令"
                        }
                    },
                    "required": ["chapter", "instruction"]
                }
            )
        ]

        self.llm_client.set_tools(tool_defs)

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        style_rules = self._load_style_rules()
        iron_rules = self._load_iron_rules()

        prompt = f"""你是专业的小说写作智能体（WritingAgent）。
你的目标是协助用户完成小说章节的创作。

【可用工具】
- query_memory: 当你需要查询角色、世界观或任何故事背景信息时使用。
  输入: {{"query": "角色名或地点名"}}
  输出: 相关角色/世界观档案文本

- write_draft: 根据给定的大纲和上下文，创作新的文本。
  输入: {{"chapter": 章节号, "outline": "章节大纲"}}
  输出: 生成的章节草稿

- revise_draft: 根据指令，修改已有的文本。
  输入: {{"chapter": 章节号, "instruction": "修改指令"}}
  输出: 修改后的草稿

【行为规则】
1. 始终遵循 ReAct 框架进行推理和行动
2. 每次行动前先思考（Thought）
3. 确保生成内容符合小说风格设定
4. 保持角色性格一致性
5. 及时埋设和回收伏笔

【写作风格】
{style_rules or "使用流畅的叙事风格，注重人物刻画和情节推进。"}

【本章铁律】
{iron_rules or "无特殊限制。"}
"""
        return prompt

    def _load_style_rules(self) -> Optional[str]:
        """加载写作风格规则"""
        return None

    def _load_iron_rules(self) -> list[str]:
        """加载本章铁律"""
        return []

    def _tool_query_memory(self, query: str) -> str:
        """工具：查询记忆"""
        return self.memory_retriever.retrieve(query)

    def _tool_write_draft(self, chapter: int, outline: str) -> str:
        """工具：写章节草稿（调用 LLM 生成）"""
        style_rules = self._load_style_rules() or "古龙式冷峻风格，短句为主，环境渲染意境"

        full_index = self.memory_retriever.get_full_index()

        prompt = f"""你是专业的小说作家。

【记忆索引】
{full_index}

请根据以下素材创作小说章节：

{outline}

写作要求：
1. 描写生动细腻，营造氛围
2. 符合古龙式冷峻风格
3. 注重人物刻画和心理描写
4. 保持角色性格一致
5. 直接输出小说内容，不需要任何说明

小说内容："""

        try:
            if not self.llm_client.config.api_key:
                draft = f"[API Key 未配置] 正在使用模拟输出。\n\n雨滴落在破庙的残瓦上，发出清脆的声响。\n\n林清瑶站在庙门前，剑鞘轻叩腰间，发出细微的金属碰撞声。她的衣衫已经湿透，雨水顺着发丝滑落，但她的眼神依然如剑锋般锐利。\n\n'十年了。'她在心中默念，'我终于找到了这里。'\n\n..."
                self._update_memory_after_write(draft)
                return draft

            response = self.llm_client.call(prompt, temperature=0.8, max_tokens=2000)
            content = response.content

            if not content:
                return "[LLM 返回空内容]"

            self._update_memory_after_write(content)
            return content

        except Exception as e:
            logger.error(f"写作失败: {e}")
            return f"[写作失败: {str(e)}]\n\n请检查 API 配置和网络连接。"

    def _update_memory_after_write(self, draft_content: str) -> None:
        """章节写作后自动更新记忆（Auto Dream）"""
        try:
            stats = self.memory_integrator.extract_and_update_memory(draft_content)
            if stats["new_characters"] > 0 or stats["new_locations"] > 0 or stats["new_foreshadowing"] > 0:
                logger.info(f"记忆更新完成: 新增角色{stats['new_characters']}个, 新增地点{stats['new_locations']}个, 新增伏笔{stats['new_foreshadowing']}个, 回收伏笔{stats['resolved_foreshadowing']}个")
        except Exception as e:
            logger.warning(f"记忆更新失败: {e}")

    def _tool_revise_draft(self, chapter: int, instruction: str) -> str:
        """工具：修订章节"""
        return f"[第{chapter}章修订]\n\n根据指令：{instruction}\n\n[修订后的内容]"

    def execute_task(self, task: WritingTask) -> WritingResult:
        """执行写作任务

        Args:
            task: 写作任务

        Returns:
            WritingResult: 执行结果
        """
        self.session_state.current_chapter = task.chapter

        system_prompt = self.get_system_prompt()
        user_message = self._build_task_message(task)

        try:
            result, history = self.react_loop.run(user_message, system_prompt)
            return WritingResult(
                success=True,
                content=result,
                task_type=task.task_type,
                history=history
            )
        except Exception as e:
            logger.error(f"任务执行失败: {e}")
            return WritingResult(
                success=False,
                content=None,
                task_type=task.task_type,
                error=str(e)
            )

    def _build_task_message(self, task: WritingTask) -> str:
        """构建任务消息"""
        messages = {
            "write": f"请写第{task.chapter}章。\n大纲：{task.content}",
            "continue": f"请继续写第{task.chapter}章。\n任务：{task.content}",
            "revise": f"请修改第{task.chapter}章。\n指令：{task.content}",
            "expand": f"请扩展以下大纲为详细章节：\n{task.content}"
        }
        return messages.get(task.task_type, task.content)

    def process_instruction(self, instruction: str) -> dict[str, Any]:
        """处理用户指令（高级接口）"""
        task = self._parse_instruction(instruction)
        result = self.execute_task(task)

        return {
            "success": result.success,
            "content": result.content,
            "task_type": result.task_type,
            "history": result.history,
            "error": result.error
        }

    def direct_write(self, outline: str, chapter: int = 1) -> str:
        """直接写作（绕过 ReAct 循环，用于测试）"""
        return self._tool_write_draft(chapter, outline)

    def _parse_instruction(self, instruction: str) -> WritingTask:
        """解析用户指令为写作任务"""
        instruction_lower = instruction.lower()

        if "写" in instruction and "章" in instruction:
            import re
            match = re.search(r'第([\d]+)章', instruction)
            chapter = int(match.group(1)) if match else 1
            return WritingTask(
                task_type="write",
                content=instruction,
                chapter=chapter
            )
        elif "继续" in instruction or "续写" in instruction:
            return WritingTask(
                task_type="continue",
                content=instruction,
                chapter=self.session_state.current_chapter or 1
            )
        elif any(kw in instruction for kw in ["修改", "改", "调整"]):
            return WritingTask(
                task_type="revise",
                content=instruction,
                chapter=self.session_state.current_chapter or 1
            )
        elif "大纲" in instruction:
            return WritingTask(
                task_type="expand",
                content=instruction
            )
        else:
            return WritingTask(
                task_type="write",
                content=instruction,
                chapter=self.session_state.current_chapter or 1
            )


def create_agent(project_path: str = "my_novel") -> WritingAgent:
    """工厂函数：创建写作智能体"""
    return WritingAgent(project_path=project_path)
