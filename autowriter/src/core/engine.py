"""WritingEngine 核心枢纽

负责：
- 接收和处理用户自然语言指令
- 管理单次 API 调用的完整生命周期
- 决定调用哪些工具及调用顺序
- 维护会话级别的临时状态
"""

import json
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from autowriter.config.settings import DEFAULT_CONFIG, SystemConfig


@dataclass
class SessionState:
    """会话级别的临时状态"""
    current_chapter: Optional[int] = None
    active_entities: list[str] = field(default_factory=list)
    pending_tools: list[str] = field(default_factory=list)
    last_action: Optional[str] = None
    continuation_marker: Optional[str] = None


@dataclass
class WritingContext:
    """写作上下文"""
    project_path: Path
    chapter_outline: Optional[str] = None
    style_rules: Optional[str] = None
    iron_rules: list[str] = field(default_factory=list)
    previous_summary: Optional[str] = None
    active_foreshadowing: list[str] = field(default_factory=list)


class WritingEngine:
    """小说写作引擎核心枢纽"""
    
    def __init__(
        self,
        project_path: str = "my_novel",
        config: Optional[SystemConfig] = None
    ):
        self.config = config or DEFAULT_CONFIG
        self.project_path = Path(project_path)
        self.session_state = SessionState()
        self._ensure_project_structure()
        
    def _ensure_project_structure(self) -> None:
        """确保项目目录结构存在"""
        self.project_path.mkdir(parents=True, exist_ok=True)
        system_path = self.project_path / self.config.project.system_dir
        system_path.mkdir(exist_ok=True)
        (system_path / self.config.project.memories_dir).mkdir(exist_ok=True)
        (system_path / self.config.project.drafts_dir).mkdir(exist_ok=True)
        
    def process_instruction(self, instruction: str) -> dict[str, Any]:
        """处理用户指令"""
        intent = self._parse_intent(instruction)
        
        if intent["type"] == "write":
            return self._handle_write(intent)
        elif intent["type"] == "continue":
            return self._handle_continue()
        elif intent["type"] == "query":
            return self._handle_query(intent)
        elif intent["type"] == "revise":
            return self._handle_revise(intent)
        elif intent["type"] == "expand":
            return self._handle_expand(intent)
        else:
            return {"status": "error", "message": f"未知指令类型: {intent['type']}"}
    
    def _parse_intent(self, instruction: str) -> dict[str, Any]:
        """解析用户指令意图"""
        instruction_lower = instruction.lower()
        
        if "写" in instruction and "章" in instruction:
            chapter = self._extract_chapter_number(instruction)
            return {"type": "write", "chapter": chapter, "raw": instruction}
        elif "继续" in instruction or "续写" in instruction:
            return {"type": "continue", "raw": instruction}
        elif any(kw in instruction for kw in ["查询", "问", "什么", "多少"]):
            return {"type": "query", "query": instruction, "raw": instruction}
        elif any(kw in instruction for kw in ["修改", "改", "调整"]):
            return {"type": "revise", "content": instruction, "raw": instruction}
        elif any(kw in instruction for kw in ["大纲", "扩展", "细化"]):
            return {"type": "expand", "content": instruction, "raw": instruction}
        else:
            return {"type": "unknown", "raw": instruction}
    
    def _extract_chapter_number(self, instruction: str) -> Optional[int]:
        """提取章节号"""
        import re
        match = re.search(r'第([一二三四五六七八九十百\d]+)章', instruction)
        if match:
            chinese_to_num = {
                '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
                '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
            }
            num_str = match.group(1)
            if num_str.isdigit():
                return int(num_str)
            return chinese_to_num.get(num_str[0], 1)
        return None
    
    def _handle_write(self, intent: dict[str, Any]) -> dict[str, Any]:
        """处理写作指令"""
        chapter = intent.get("chapter", self.session_state.current_chapter or 1)
        self.session_state.current_chapter = chapter
        
        outline = self._load_chapter_outline(chapter)
        context = WritingContext(
            project_path=self.project_path,
            chapter_outline=outline,
            style_rules=self._load_style_rules(),
        )
        
        draft = self._generate_draft(context)
        
        self._save_draft(chapter, draft)
        
        return {
            "status": "success",
            "action": "write",
            "chapter": chapter,
            "draft": draft,
            "continuation_marker": self._generate_continuation_marker(draft)
        }
    
    def _handle_continue(self) -> dict[str, Any]:
        """处理续写指令"""
        chapter = self.session_state.current_chapter or 1
        last_draft = self._load_draft(chapter)
        marker = self.session_state.continuation_marker
        
        if not last_draft:
            return {"status": "error", "message": "没有找到上一章草稿"}
        
        continuation = self._generate_continuation(last_draft, marker)
        
        self._append_draft(chapter, continuation)
        
        return {
            "status": "success",
            "action": "continue",
            "chapter": chapter,
            "continuation": continuation
        }
    
    def _handle_query(self, intent: dict[str, Any]) -> dict[str, Any]:
        """处理查询指令"""
        return {
            "status": "success",
            "action": "query",
            "result": "查询功能待实现"
        }
    
    def _handle_revise(self, intent: dict[str, Any]) -> dict[str, Any]:
        """处理修订指令"""
        return {
            "status": "success",
            "action": "revise",
            "message": "修订功能待实现"
        }
    
    def _handle_expand(self, intent: dict[str, Any]) -> dict[str, Any]:
        """处理扩展大纲指令"""
        return {
            "status": "success",
            "action": "expand",
            "message": "大纲扩展功能待实现"
        }
    
    def _load_chapter_outline(self, chapter: int) -> Optional[str]:
        """加载章节大纲"""
        outline_path = self.config.get_outline_path(str(self.project_path))
        if outline_path.exists():
            content = outline_path.read_text(encoding="utf-8")
            return self._extract_chapter_from_outline(content, chapter)
        return None
    
    def _extract_chapter_from_outline(self, content: str, chapter: int) -> Optional[str]:
        """从大纲中提取指定章节"""
        import re
        pattern = rf'第[一二三四五六七八九十百\d]+章[^\n]*'
        chapters = re.split(r'(?=第[一二三四五六七八九十百\d]+章)', content)
        for ch in chapters:
            if re.search(rf'第{"一二三四五六七八九十百"[chapter-1] if chapter <= 10 else str(chapter)}章', ch):
                return ch.strip()
        return None
    
    def _load_style_rules(self) -> Optional[str]:
        """加载写作风格规则"""
        return None
    
    def _generate_draft(self, context: WritingContext) -> str:
        """生成章节草稿（最简实现）"""
        prompt = self._build_simple_prompt(context)
        return f"[第{self.session_state.current_chapter}章草稿]\n\n系统提示：请配置 LLM API 以生成实际内容。\n\n大纲: {context.chapter_outline or '未提供大纲'}"
    
    def _build_simple_prompt(self, context: WritingContext) -> str:
        """构建简单写作 Prompt"""
        parts = []
        if context.style_rules:
            parts.append(f"【写作风格】\n{context.style_rules}")
        if context.chapter_outline:
            parts.append(f"【章节大纲】\n{context.chapter_outline}")
        if context.previous_summary:
            parts.append(f"【前情提要】\n{context.previous_summary}")
        return "\n\n".join(parts)
    
    def _generate_continuation(
        self, 
        previous_draft: str, 
        marker: Optional[str] = None
    ) -> str:
        """生成续写内容"""
        if marker:
            return f"\n\n[MARKER]: {marker}\n\n[续写内容]\n\n系统提示：请配置 LLM API 以生成实际内容。"
        return "\n\n[续写内容]\n\n系统提示：请配置 LLM API 以生成实际内容。"
    
    def _generate_continuation_marker(self, draft: str) -> str:
        """生成续写标记"""
        lines = draft.strip().split('\n')
        last_line = lines[-1] if lines else ""
        return json.dumps({
            "last_sentence": last_line[:100],
            "unfinished_action": "待补充",
            "next_event": "待补充"
        }, ensure_ascii=False)
    
    def _save_draft(self, chapter: int, content: str) -> None:
        """保存章节草稿"""
        draft_path = self.config.get_drafts_path(str(self.project_path))
        draft_file = draft_path / f"chapter_{chapter:03d}.md"
        draft_file.write_text(content, encoding="utf-8")
    
    def _load_draft(self, chapter: int) -> Optional[str]:
        """加载章节草稿"""
        draft_path = self.config.get_drafts_path(str(self.project_path))
        draft_file = draft_path / f"chapter_{chapter:03d}.md"
        if draft_file.exists():
            return draft_file.read_text(encoding="utf-8")
        return None
    
    def _append_draft(self, chapter: int, content: str) -> None:
        """追加草稿内容"""
        current = self._load_draft(chapter) or ""
        self._save_draft(chapter, current + content)
    
    def get_session_state(self) -> dict[str, Any]:
        """获取当前会话状态"""
        return {
            "current_chapter": self.session_state.current_chapter,
            "active_entities": self.session_state.active_entities,
            "pending_tools": self.session_state.pending_tools,
            "last_action": self.session_state.last_action
        }
    
    def build_graph(self) -> StateGraph:
        """构建 LangGraph 状态机"""
        workflow = StateGraph(dict)
        
        workflow.add_node("receive", self._node_receive)
        workflow.add_node("plan", self._node_plan)
        workflow.add_node("execute", self._node_execute)
        workflow.add_node("reflect", self._node_reflect)
        workflow.add_node("save", self._node_save)
        
        workflow.set_entry_point("receive")
        workflow.add_edge("receive", "plan")
        workflow.add_edge("plan", "execute")
        workflow.add_edge("execute", "reflect")
        workflow.add_edge("reflect", END)
        workflow.add_edge("save", END)
        
        return workflow.compile()
    
    def _node_receive(self, state: dict) -> dict:
        """接收节点"""
        return state
    
    def _node_plan(self, state: dict) -> dict:
        """规划节点"""
        return state
    
    def _node_execute(self, state: dict) -> dict:
        """执行节点"""
        return state
    
    def _node_reflect(self, state: dict) -> dict:
        """反思节点"""
        return state
    
    def _node_save(self, state: dict) -> dict:
        """保存节点"""
        return state


def create_engine(project_path: str = "my_novel") -> WritingEngine:
    """工厂函数：创建写作引擎"""
    return WritingEngine(project_path=project_path)
