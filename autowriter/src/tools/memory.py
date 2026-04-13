"""query_memory 工具

使用 MemoryRetriever 实现真实检索，返回格式化的上下文。
"""

from typing import Dict, Any
from autowriter.src.memory import MemoryRetriever


class QueryMemoryTool:
    """查询记忆工具"""

    name = "query_memory"
    description = "当需要查询角色、世界观或任何故事背景信息时使用。输入查询字符串，返回相关的角色/世界观档案文本。"

    def __init__(self, novel_path: str):
        self.retriever = MemoryRetriever(novel_path)

    def execute(self, query: str) -> str:
        """执行查询

        Args:
            query: 查询字符串（如角色名、地点名等）

        Returns:
            检索到的上下文文本（不超过 500 字）
        """
        return self.retriever.retrieve(query)

    def get_full_index(self) -> str:
        """获取完整的 L1 索引（用于 API 调用注入）"""
        return self.retriever.get_full_index()

    def get_schema(self) -> Dict[str, Any]:
        """获取工具 schema（用于 LLM 工具调用）"""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "查询字符串，可以是角色名、地点名、事件名等"
                    }
                },
                "required": ["query"]
            }
        }
