"""系统配置管理"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLM API 配置 - 支持 MiniMax Anthropic 兼容模式"""
    provider: str = "minimax"
    model: str = "MiniMax-M2.7"
    api_key: Optional[str] = Field(default=None, description="从环境变量加载")
    base_url: str = "https://api.minimaxi.com/anthropic"
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 120

    def __init__(self, **data):
        super().__init__(**data)
        self._load_from_env()

    def _load_from_env(self) -> None:
        """从环境变量加载 MiniMax Anthropic 配置"""
        if api_key := os.getenv("ANTHROPIC_API_KEY"):
            self.api_key = api_key
        elif api_key := os.getenv("MINIMAX_API_KEY"):
            self.api_key = api_key
        elif api_key := os.getenv("MINIMAX_start"):
            self.api_key = api_key
        if base_url := os.getenv("ANTHROPIC_BASE_URL"):
            self.base_url = base_url
        elif base_url := os.getenv("MINIMAX_BASE_URL"):
            self.base_url = base_url
        if model := os.getenv("MINIMAX_MODEL"):
            self.model = model
        elif model := os.getenv("MINIMAX_START_MODEL"):
            self.model = model
        if temp := os.getenv("MINIMAX_TEMPERATURE"):
            self.temperature = float(temp)
        if tokens := os.getenv("MINIMAX_MAX_TOKENS"):
            self.max_tokens = int(tokens)


class ProjectConfig(BaseModel):
    """项目配置"""
    novel_dir: str = "my_novel"
    system_dir: str = ".novel"
    memory_index: str = "memory_index.md"
    memories_dir: str = "memories"
    drafts_dir: str = "drafts"
    state_file: str = "state.json"
    outline_file: str = "outline.md"
    novel_file: str = "novel.md"


class MemoryConfig(BaseModel):
    """记忆系统配置"""
    index_max_chars: int = 500
    pointer_max_chars: int = 150
    retrieval_trigger_per_chapter: bool = True


class WritingConfig(BaseModel):
    """写作引擎配置"""
    compression_threshold: int = 3000
    compression_reserve: int = 500
    compression_summary_chars: int = 200
    continuation_marker_start: str = "[续写标记]"
    continuation_marker_end: str = "[/续写标记]"


class ValidationConfig(BaseModel):
    """验证流水线配置"""
    auto_validate: bool = True
    check_consistency: bool = True
    check_foreshavioring: bool = True
    check_dialogue: bool = True


class ReActConfig(BaseModel):
    """ReAct 循环配置"""
    max_iterations: int = 50
    thinking_threshold: int = 3
    error_retry_count: int = 3


class SystemConfig(BaseModel):
    """系统全局配置"""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    writing: WritingConfig = Field(default_factory=WritingConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    react: ReActConfig = Field(default_factory=ReActConfig)

    @classmethod
    def load_from_env(cls) -> "SystemConfig":
        """从环境变量加载完整配置"""
        return cls()

    def get_project_path(self, project_name: str = "my_novel") -> Path:
        """获取小说项目根目录"""
        return Path(project_name)

    def get_system_path(self, project_name: str = "my_novel") -> Path:
        """获取系统内部状态目录"""
        return self.get_project_path(project_name) / self.project.system_dir

    def get_memory_index_path(self, project_name: str = "my_novel") -> Path:
        """获取索引文件路径"""
        return self.get_system_path(project_name) / self.project.memory_index

    def get_memories_path(self, project_name: str = "my_novel") -> Path:
        """获取详情记忆目录"""
        return self.get_system_path(project_name) / self.project.memories_dir

    def get_drafts_path(self, project_name: str = "my_novel") -> Path:
        """获取草稿目录"""
        return self.get_system_path(project_name) / self.project.drafts_dir

    def get_state_path(self, project_name: str = "my_novel") -> Path:
        """获取状态文件路径"""
        return self.get_system_path(project_name) / self.project.state_file

    def get_outline_path(self, project_name: str = "my_novel") -> Path:
        """获取大纲文件路径"""
        return self.get_project_path(project_name) / self.project.outline_file

    def get_novel_path(self, project_name: str = "my_novel") -> Path:
        """获取成品文件路径"""
        return self.get_project_path(project_name) / self.project.novel_file


DEFAULT_CONFIG = SystemConfig.load_from_env()
