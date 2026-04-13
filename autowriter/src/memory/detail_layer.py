"""L2 详情层管理模块

管理 memories/*.md 文件的读写。
使用 Markdown 标题 (# 标题) 作为检索锚点。
"""

import os
import re
from typing import Optional


class DetailLayer:
    """L2 详情层管理类"""

    VALID_FILES = {"characters.md", "worldview.md", "timeline.md", "foreshadowing.md"}

    def __init__(self, novel_path: str):
        self.novel_path = novel_path
        self.memories_dir = os.path.join(novel_path, ".novel", "memories")
        self._ensure_memories_dir()

    def _ensure_memories_dir(self) -> None:
        """确保 memories 目录存在"""
        os.makedirs(self.memories_dir, exist_ok=True)

    def _get_file_path(self, file: str) -> str:
        """获取文件的完整路径"""
        if not file.endswith(".md"):
            file = file + ".md"
        return os.path.join(self.memories_dir, file)

    def get_detail(self, file: str, anchor: str) -> Optional[str]:
        """根据锚点获取详情内容

        Args:
            file: 文件名（不含路径），如 "characters.md" 或 "characters"
            anchor: 锚点标题（不含 #），如 "林清瑶"

        Returns:
            锚点下的内容块，如果不存在则返回 None
        """
        file_path = self._get_file_path(file)

        if not os.path.exists(file_path):
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return self._extract_anchor_content(content, anchor)

    def _extract_anchor_content(self, content: str, anchor: str) -> Optional[str]:
        """从 Markdown 内容中提取指定锚点的内容块

        Args:
            content: Markdown 文件完整内容
            anchor: 要提取的锚点标题

        Returns:
            锚点下的内容块，直到遇到下一个同级或更高级标题
        """
        lines = content.split("\n")

        result_lines = []
        in_anchor = False
        current_level = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            if stripped.startswith("#"):
                heading_match = re.match(r"^(#+)\s+(.+)$", stripped)
                if heading_match:
                    heading_text = heading_match.group(2).strip()
                    heading_level = len(heading_match.group(1))

                    if heading_text == anchor:
                        in_anchor = True
                        current_level = heading_level
                        result_lines.append(stripped)
                    elif in_anchor:
                        if heading_level <= current_level:
                            in_anchor = False
                            break
                continue

            if in_anchor:
                result_lines.append(stripped)

        if not result_lines:
            return None

        return "\n".join(result_lines)

    def update_detail(self, file: str, anchor: str, content: str) -> bool:
        """在指定锚点下更新内容

        如果锚点不存在则创建。

        Args:
            file: 文件名
            anchor: 锚点标题
            content: 要更新的内容

        Returns:
            True if successful
        """
        file_path = self._get_file_path(file)

        if os.path.exists(file_path):
            existing_content = self._read_file(file_path)
        else:
            existing_content = ""

        updated_content = self._update_anchor_content(existing_content, anchor, content)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

        return True

    def _read_file(self, file_path: str) -> str:
        """读取文件内容"""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _update_anchor_content(self, content: str, anchor: str, new_content: str) -> str:
        """更新或添加锚点内容"""
        lines = content.split("\n") if content else []
        target_heading = f"# {anchor}"

        for i, line in enumerate(lines):
            if line.strip().startswith("#") and anchor in line:
                heading_match = re.match(r"^(#+)\s+(.+)$", line.strip())
                if heading_match and heading_match.group(2).strip() == anchor:
                    start_idx = i + 1
                    current_level = len(heading_match.group(1))

                    end_idx = len(lines)
                    for j in range(i + 1, len(lines)):
                        stripped = lines[j].strip()
                        if stripped.startswith("#"):
                            next_match = re.match(r"^(#+)\s+", stripped)
                            if next_match and len(next_match.group(1)) <= current_level:
                                end_idx = j
                                break

                    new_lines = []
                    new_lines.extend(lines[:start_idx])
                    new_lines.append("")
                    new_lines.extend(new_content.split("\n"))
                    new_lines.append("")
                    new_lines.extend(lines[end_idx:])

                    return "\n".join(new_lines)

        if lines and lines[-1].strip():
            lines.append("")

        lines.append(target_heading)
        lines.append("")
        lines.extend(new_content.split("\n"))

        return "\n".join(lines)

    def create_anchor(self, file: str, anchor: str, content: str) -> bool:
        """在文件末尾创建新的锚点条目

        Args:
            file: 文件名
            anchor: 锚点标题
            content: 锚点内容

        Returns:
            True if successful
        """
        return self.update_detail(file, anchor, content)

    def anchor_exists(self, file: str, anchor: str) -> bool:
        """检查锚点是否存在"""
        detail = self.get_detail(file, anchor)
        return detail is not None

    def list_anchors(self, file: str) -> list:
        """列出文件中所有锚点"""
        file_path = self._get_file_path(file)

        if not os.path.exists(file_path):
            return []

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        anchors = []
        for line in content.split("\n"):
            match = re.match(r"^#+\s+(.+)$", line.strip())
            if match:
                anchors.append(match.group(1).strip())

        return anchors

    def get_file_path(self, file: str) -> str:
        """获取文件的完整路径"""
        return self._get_file_path(file)
