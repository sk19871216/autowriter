"""Auto Dream 记忆整合模块

在章节写作完成后自动整合记忆：
1. 使用 LLM 从新章节草稿中提取结构化信息
2. 检测伏笔回收
3. 自动更新记忆文件
"""

import re
from typing import List, Dict, Tuple, Optional
from .index_layer import IndexLayer
from .detail_layer import DetailLayer
from .state_layer import StateLayer
from autowriter.src.llm.client import LLMClient


EXTRACTION_PROMPT = """请从以下小说片段中提取：
1. 新出现的角色名（以及简要特征）
2. 新出现的地点/场景
3. 可能埋下的伏笔

输出格式：
角色: 名称 | 特征描述
地点: 名称 | 描述
伏笔: 内容描述

如果没有某类信息，请写"无"。

小说片段：
{draft_text}

提取结果："""


class ExtractedEntity:
    """提取的实体"""

    def __init__(self, entity_type: str, name: str, description: str = ""):
        self.entity_type = entity_type
        self.name = name
        self.description = description

    def __repr__(self):
        return f"ExtractedEntity({self.entity_type}, {self.name}, {self.description})"


class MemoryIntegrator:
    """记忆整合器 - 实现 Auto Dream 功能"""

    TYPE_FILE_MAP = {
        "char": "characters.md",
        "world": "worldview.md",
        "event": "timeline.md",
        "foreshadow": "foreshadowing.md"
    }

    def __init__(self, novel_path: str):
        self.novel_path = novel_path
        self.index_layer = IndexLayer(novel_path)
        self.detail_layer = DetailLayer(novel_path)
        self.state_layer = StateLayer(novel_path)
        self.llm_client = LLMClient()

    def extract_and_update_memory(self, draft_text: str) -> Dict[str, int]:
        """从草稿中提取信息并更新记忆

        Args:
            draft_text: 章节草稿文本

        Returns:
            统计信息，包含新增角色、地点、伏笔数量
        """
        extracted = self._extract_entities(draft_text)

        stats = {
            "new_characters": 0,
            "new_locations": 0,
            "new_foreshadowing": 0,
            "resolved_foreshadowing": 0
        }

        for entity in extracted:
            if entity.entity_type == "char":
                if self._add_character(entity):
                    stats["new_characters"] += 1
            elif entity.entity_type == "world":
                if self._add_location(entity):
                    stats["new_locations"] += 1
            elif entity.entity_type == "foreshadow":
                if self._add_foreshadow(entity):
                    stats["new_foreshadowing"] += 1

        stats["resolved_foreshadowing"] = self._check_foreshadowing_resolution(draft_text)

        return stats

    def _extract_entities(self, draft_text: str) -> List[ExtractedEntity]:
        """使用 LLM 从草稿中提取实体

        Args:
            draft_text: 草稿文本

        Returns:
            提取的实体列表
        """
        prompt = EXTRACTION_PROMPT.format(draft_text=draft_text[:3000])

        try:
            response = self.llm_client.create_message(
                system="你是一个专业的小说分析助手，擅长提取小说中的关键信息。",
                user_message=prompt,
                max_tokens=1000
            )

            response_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    response_text += block.text

            return self._parse_extraction_result(response_text)
        except Exception as e:
            return []

    def _parse_extraction_result(self, text: str) -> List[ExtractedEntity]:
        """解析 LLM 返回的提取结果

        Args:
            text: LLM 返回的文本

        Returns:
            解析后的实体列表
        """
        entities = []

        for line in text.split("\n"):
            line = line.strip()
            if not line or line == "无":
                continue

            if line.startswith("角色:"):
                content = line[3:].strip()
                name, desc = self._parse_entity_line(content)
                if name:
                    entities.append(ExtractedEntity("char", name, desc))

            elif line.startswith("地点:"):
                content = line[3:].strip()
                name, desc = self._parse_entity_line(content)
                if name:
                    entities.append(ExtractedEntity("world", name, desc))

            elif line.startswith("伏笔:"):
                content = line[3:].strip()
                if content and content != "无":
                    entities.append(ExtractedEntity("foreshadow", content, ""))

        return entities

    def _parse_entity_line(self, content: str) -> Tuple[Optional[str], str]:
        """解析实体行

        Args:
            content: 行内容（格式：名称 | 描述）

        Returns:
            (名称, 描述) 元组
        """
        if "|" in content:
            parts = content.split("|", 1)
            name = parts[0].strip()
            desc = parts[1].strip() if len(parts) > 1 else ""
            return name, desc
        return content.strip(), ""

    def _add_character(self, entity: ExtractedEntity) -> bool:
        """添加角色到记忆

        Args:
            entity: 角色实体

        Returns:
            True if added, False if already exists
        """
        if self.index_layer.exists(entity.name):
            return False

        file = self.TYPE_FILE_MAP["char"]
        anchor = entity.name
        content = f"- 身份：{entity.description}\n- 首次出现：待补充"

        self.detail_layer.create_anchor(file, anchor, content)

        desc = entity.description[:30] if entity.description else "新角色"
        anchor_path = f"memories/{file}#{anchor}"
        self.index_layer.add_entry("char", entity.name, desc, anchor_path)

        self.state_layer.update_character_status(entity.name, location="未知", condition="正常")

        return True

    def _add_location(self, entity: ExtractedEntity) -> bool:
        """添加地点到记忆

        Args:
            entity: 地点实体

        Returns:
            True if added, False if already exists
        """
        if self.index_layer.exists(entity.name):
            return False

        file = self.TYPE_FILE_MAP["world"]
        anchor = entity.name
        content = f"- 描述：{entity.description}\n- 首次出现：待补充"

        self.detail_layer.create_anchor(file, anchor, content)

        desc = entity.description[:30] if entity.description else "新地点"
        anchor_path = f"memories/{file}#{anchor}"
        self.index_layer.add_entry("world", entity.name, desc, anchor_path)

        return True

    def _add_foreshadow(self, entity: ExtractedEntity) -> bool:
        """添加伏笔到记忆

        Args:
            entity: 伏笔实体

        Returns:
            True if added, False if already exists or no description
        """
        if not entity.name:
            return False

        existing = self.state_layer.get_pending_foreshadowing()
        for fs in existing:
            if fs.get("id") == entity.name:
                return False

        self.state_layer.add_foreshadowing(entity.name, entity.description)

        if not self.detail_layer.anchor_exists(self.TYPE_FILE_MAP["foreshadow"], entity.name):
            file = self.TYPE_FILE_MAP["foreshadow"]
            content = f"- 提示：{entity.description}\n- 状态：未回收"
            self.detail_layer.create_anchor(file, entity.name, content)

        anchor_path = f"memories/{self.TYPE_FILE_MAP['foreshadow']}#{entity.name}"
        self.index_layer.add_entry("foreshadow", entity.name, entity.description[:30], anchor_path)

        return True

    def _check_foreshadowing_resolution(self, draft_text: str) -> int:
        """检查伏笔回收

        Args:
            draft_text: 草稿文本

        Returns:
            回收的伏笔数量
        """
        pending = self.state_layer.get_pending_foreshadowing()
        resolved_count = 0

        for fs in pending:
            if self._contains_foreshadow_mention(draft_text, fs.get("id", "")):
                self.state_layer.resolve_foreshadowing(fs.get("id", ""))
                resolved_count += 1

        return resolved_count

    def _contains_foreshadow_mention(self, text: str, foreshadow_id: str) -> bool:
        """检查文本是否提及伏笔

        Args:
            text: 文本
            foreshadow_id: 伏笔标识

        Returns:
            True if mentioned
        """
        if not foreshadow_id:
            return False

        return foreshadow_id in text
