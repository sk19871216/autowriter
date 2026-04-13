"""L1 索引层管理模块

管理 memory_index.md 的读写和检索。
格式：类型 名称 | 简短描述 | 详情文件路径#锚点
每行不超过 150 字符。
"""

import os
import re
from typing import List, Tuple, Optional, Dict, Any


class IndexEntry:
    """索引条目"""

    VALID_TYPES = {"char", "world", "event", "foreshadow"}
    MAX_LINE_LENGTH = 150

    def __init__(self, entry_type: str, name: str, description: str, anchor: str):
        if entry_type not in self.VALID_TYPES:
            raise ValueError(f"Invalid type: {entry_type}. Must be one of {self.VALID_TYPES}")
        self.entry_type = entry_type
        self.name = name
        self.description = description
        self.anchor = anchor

    def to_line(self) -> str:
        line = f"{self.entry_type} {self.name} | {self.description} | {self.anchor}"
        if len(line) > self.MAX_LINE_LENGTH:
            raise ValueError(f"Entry line exceeds {self.MAX_LINE_LENGTH} characters: {line}")
        return line

    @classmethod
    def from_line(cls, line: str) -> "IndexEntry":
        parts = line.split("|")
        if len(parts) != 3:
            raise ValueError(f"Invalid entry format: {line}")

        type_and_name = parts[0].strip()
        type_parts = type_and_name.split(" ", 1)
        if len(type_parts) != 2:
            raise ValueError(f"Invalid type/name format: {type_and_name}")

        entry_type = type_parts[0]
        name = type_parts[1]
        description = parts[1].strip()
        anchor = parts[2].strip()

        return cls(entry_type, name, description, anchor)

    def to_dict(self) -> Dict[str, str]:
        return {
            "type": self.entry_type,
            "name": self.name,
            "description": self.description,
            "anchor": self.anchor
        }


class IndexLayer:
    """L1 索引层管理类"""

    def __init__(self, novel_path: str):
        self.novel_path = novel_path
        self.index_file = os.path.join(novel_path, ".novel", "memory_index.md")
        self._entries: List[IndexEntry] = []
        self._load()

    def _load(self) -> None:
        """从文件加载索引"""
        self._entries = []
        if not os.path.exists(self.index_file):
            return

        with open(self.index_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    entry = IndexEntry.from_line(line)
                    self._entries.append(entry)
                except ValueError:
                    continue

    def _save(self) -> None:
        """保存索引到文件"""
        os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
        with open(self.index_file, "w", encoding="utf-8") as f:
            f.write("# Memory Index\n\n")
            for entry in self._entries:
                f.write(entry.to_line() + "\n")

    def add_entry(self, entry_type: str, name: str, description: str, anchor: str) -> bool:
        """添加索引条目

        Returns:
            True if added, False if entry with same name already exists
        """
        if self._find_by_name(name) is not None:
            return False

        entry = IndexEntry(entry_type, name, description, anchor)
        self._entries.append(entry)
        self._save()
        return True

    def remove_entry(self, name: str) -> bool:
        """删除索引条目

        Returns:
            True if removed, False if not found
        """
        for i, entry in enumerate(self._entries):
            if entry.name == name:
                self._entries.pop(i)
                self._save()
                return True
        return False

    def _find_by_name(self, name: str) -> Optional[IndexEntry]:
        """根据名称查找条目"""
        for entry in self._entries:
            if entry.name == name:
                return entry
        return None

    def search(self, query: str, top_k: int = 3) -> List[Tuple[IndexEntry, float]]:
        """搜索相似条目

        Args:
            query: 查询字符串
            top_k: 返回前 k 个最相似的结果

        Returns:
            List of (entry, score) tuples, sorted by score descending
        """
        query_words = set(query.lower().split())
        results = []

        for entry in self._entries:
            score = self._calculate_similarity(query_words, entry)
            results.append((entry, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def _calculate_similarity(self, query_words: set, entry: IndexEntry) -> float:
        """计算查询词与条目的相似度

        使用关键词重叠率计算
        """
        entry_words = set()
        entry_words.update(entry.name.lower().split())
        entry_words.update(entry.description.lower().split())
        entry_words.update(entry.entry_type.lower().split())

        if not query_words or not entry_words:
            return 0.0

        intersection = query_words & entry_words
        union = query_words | entry_words
        return len(intersection) / len(union)

    def update_entry(self, name: str, **kwargs) -> bool:
        """更新索引条目

        Args:
            name: 条目名称
            **kwargs: 要更新的字段（description）

        Returns:
            True if updated, False if not found
        """
        entry = self._find_by_name(name)
        if entry is None:
            return False

        if "description" in kwargs:
            entry.description = kwargs["description"]
        if "name" in kwargs:
            entry.name = kwargs["name"]
        if "anchor" in kwargs:
            entry.anchor = kwargs["anchor"]

        self._save()
        return True

    def get_all_entries(self) -> List[IndexEntry]:
        """获取所有索引条目"""
        return self._entries.copy()

    def get_entries_by_type(self, entry_type: str) -> List[IndexEntry]:
        """获取指定类型的所有条目"""
        return [e for e in self._entries if e.entry_type == entry_type]

    def exists(self, name: str) -> bool:
        """检查条目是否存在"""
        return self._find_by_name(name) is not None
