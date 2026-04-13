"""核心状态管理模块"""

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class InstructionType(str, Enum):
    """指令类型枚举"""
    WRITE = "write"
    CONTINUE = "continue"
    REVISE = "revise"
    QUERY = "query"
    EXPAND = "expand"
    UNKNOWN = "unknown"


class ChapterStatus(str, Enum):
    """章节状态枚举"""
    PLANNED = "planned"
    DRAFTING = "drafting"
    DRAFTED = "drafted"
    VALIDATING = "validating"
    VALIDATED = "validated"
    REVISING = "revising"
    COMPLETED = "completed"
    NEEDS_REVISION = "needs_revision"


class WritingState(BaseModel):
    """写作状态"""
    project_path: str
    current_chapter: Optional[int] = None
    total_chapters: Optional[int] = None
    writing_style: Optional[str] = None
    iron_rules: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ChapterState(BaseModel):
    """单章状态"""
    chapter_number: int
    status: ChapterStatus = ChapterStatus.PLANNED
    outline: Optional[str] = None
    draft_path: Optional[str] = None
    word_count: int = 0
    active_entities: list[str] = Field(default_factory=list)
    introduced_foreshadowing: list[str] = Field(default_factory=list)
    resolved_foreshadowing: list[str] = Field(default_factory=list)
    inconsistencies: list[dict] = Field(default_factory=list)
    validation_report: Optional[dict] = None
    needs_revision: bool = False
    revision_notes: Optional[str] = None


class SessionState(BaseModel):
    """会话状态"""
    session_id: str
    project_path: str
    current_chapter: Optional[int] = None
    active_entities: list[str] = Field(default_factory=list)
    pending_tools: list[str] = Field(default_factory=list)
    last_action: Optional[str] = None
    continuation_marker: Optional[dict] = None
    instruction_history: list[dict] = Field(default_factory=list)
    
    def add_instruction(self, instruction: str, intent_type: str):
        """添加指令到历史"""
        self.instruction_history.append({
            "instruction": instruction,
            "intent_type": intent_type,
            "timestamp": datetime.now().isoformat()
        })


class ToolCallRecord(BaseModel):
    """工具调用记录"""
    tool_name: str
    parameters: dict
    result: Optional[Any] = None
    success: bool = True
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class MemoryState(BaseModel):
    """记忆系统状态"""
    memory_index_modified: bool = False
    last_auto_dream: Optional[datetime] = None
    active_characters: list[str] = Field(default_factory=list)
    active_locations: list[str] = Field(default_factory=list)
    unresolved_foreshadowing: list[str] = Field(default_factory=list)


class ValidationState(BaseModel):
    """验证状态"""
    auto_validate: bool = True
    last_validation: Optional[datetime] = None
    check_consistency: bool = True
    check_foreshadowing: bool = True
    check_dialogue: bool = True
    validation_results: list[dict] = Field(default_factory=list)


class EngineState(BaseModel):
    """引擎全局状态"""
    writing: WritingState
    chapter: Optional[ChapterState] = None
    session: Optional[SessionState] = None
    memory: MemoryState = Field(default_factory=MemoryState)
    validation: ValidationState = Field(default_factory=ValidationState)
    
    @classmethod
    def create_new(cls, project_path: str, session_id: str) -> "EngineState":
        """创建新的引擎状态"""
        return cls(
            writing=WritingState(project_path=project_path),
            session=SessionState(session_id=session_id, project_path=project_path)
        )


class StateManager:
    """状态管理器"""
    
    def __init__(self, state: EngineState):
        self.state = state
    
    def update_chapter(self, chapter_state: ChapterState):
        """更新章节状态"""
        self.state.chapter = chapter_state
    
    def update_session(self, session_state: SessionState):
        """更新会话状态"""
        self.state.session = session_state
    
    def add_tool_call(self, record: ToolCallRecord):
        """添加工具调用记录"""
        if self.state.session:
            pass
    
    def mark_memory_modified(self):
        """标记记忆已修改"""
        self.state.memory.memory_index_modified = True
    
    def update_validation_result(self, result: dict):
        """更新验证结果"""
        self.state.validation.validation_results.append(result)
        self.state.validation.last_validation = datetime.now()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return self.state.model_dump()
    
    @classmethod
    def from_dict(cls, data: dict) -> "StateManager":
        """从字典创建"""
        state = EngineState(**data)
        return cls(state)
