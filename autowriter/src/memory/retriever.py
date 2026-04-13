"""检索与注入机制模块

组合 IndexLayer, DetailLayer, StateLayer 实现统一检索接口。
返回不超过 500 字的上下文资料包。
"""

from typing import List, Tuple, Optional
from .index_layer import IndexLayer, IndexEntry
from .detail_layer import DetailLayer
from .state_layer import StateLayer


class MemoryRetriever:
    """记忆检索器 - 组合三层记忆实现统一检索"""

    MAX_CONTEXT_LENGTH = 500

    TYPE_KEYWORDS = {
        "char": ["角色", "人物", "角色名", "人物名", "谁", "角色", "character"],
        "world": ["地点", "场景", "地方", "位置", "世界", "场景", "world", "location", "place"],
        "event": ["事件", "发生", "事情", "经过", "event"],
        "foreshadow": ["伏笔", "暗示", "预兆", "伏笔", "foreshadow"]
    }

    def __init__(self, novel_path: str):
        self.index_layer = IndexLayer(novel_path)
        self.detail_layer = DetailLayer(novel_path)
        self.state_layer = StateLayer(novel_path)

    def retrieve(self, query: str) -> str:
        """检索并返回上下文资料包

        Args:
            query: 查询字符串

        Returns:
            不超过 500 字的上下文资料包
        """
        intent = self._parse_intent(query)

        search_results = self.index_layer.search(query, top_k=3)

        if not search_results:
            return self._build_default_context()

        context_parts = []
        char_status = None
        current_length = 0

        for entry, score in search_results:
            if score < 0.1:
                continue

            detail = self._get_detail_for_entry(entry)
            if not detail:
                continue

            entry_text = f"【{entry.name}】\n{detail}"
            entry_length = len(entry_text)

            if current_length + entry_length > self.MAX_CONTEXT_LENGTH:
                remaining = self.MAX_CONTEXT_LENGTH - current_length - 10
                if remaining > 50:
                    context_parts.append(entry_text[:remaining] + "...")
                break

            context_parts.append(entry_text)
            current_length += entry_length + 2

            if entry.entry_type == "char" and char_status is None:
                char_status = self.state_layer.get_character_status(entry.name)

        if char_status:
            status_text = self._format_character_status(char_status)
            if current_length + len(status_text) <= self.MAX_CONTEXT_LENGTH:
                context_parts.append(f"【当前状态】\n{status_text}")

        if not context_parts:
            return self._build_default_context()

        return "\n\n".join(context_parts)

    def _parse_intent(self, query: str) -> str:
        """解析查询意图

        Args:
            query: 查询字符串

        Returns:
            意图类型: char, world, event, foreshadow, 或 unknown
        """
        query_lower = query.lower()
        scores = {}

        for intent_type, keywords in self.TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in query_lower)
            scores[intent_type] = score

        if max(scores.values()) > 0:
            return max(scores, key=scores.get)

        return "unknown"

    def _get_detail_for_entry(self, entry: IndexEntry) -> Optional[str]:
        """获取条目的详情内容"""
        anchor_parts = entry.anchor.split("#")
        if len(anchor_parts) != 2:
            return None

        file_path = anchor_parts[0]
        anchor = anchor_parts[1]

        if file_path.startswith("memories/"):
            file_path = file_path[9:]

        return self.detail_layer.get_detail(file_path, anchor)

    def _format_character_status(self, status: dict) -> str:
        """格式化角色状态"""
        parts = []
        if "location" in status:
            parts.append(f"位置: {status['location']}")
        if "condition" in status:
            parts.append(f"状态: {status['condition']}")
        if "inventory" in status and status["inventory"]:
            items = ", ".join(status["inventory"])
            parts.append(f"物品: {items}")
        return "\n".join(parts) if parts else ""

    def _build_default_context(self) -> str:
        """构建默认上下文"""
        return "未找到相关信息。请提供更多细节。"

    def get_full_index(self) -> str:
        """获取完整的 L1 索引（用于每次 API 调用注入）

        Returns:
            完整的索引文本
        """
        entries = self.index_layer.get_all_entries()
        lines = []
        for entry in entries:
            line = entry.to_line()
            if len(line) <= 150:
                lines.append(line)

        header = "# 记忆索引\n\n"
        return header + "\n".join(lines)

    def search_and_get_details(self, query: str) -> List[Tuple[IndexEntry, str]]:
        """搜索并获取详情

        Args:
            query: 查询字符串

        Returns:
            List of (entry, detail) tuples
        """
        search_results = self.index_layer.search(query, top_k=3)
        results = []

        for entry, score in search_results:
            if score < 0.1:
                continue
            detail = self._get_detail_for_entry(entry)
            if detail:
                results.append((entry, detail))

        return results
