"""L3 状态层管理模块

管理 state.json 的读写和状态更新。
扩展 story_state 结构：timeline, character_status, pending_foreshadowing
"""

import json
import os
from typing import Dict, List, Optional, Any


class StateLayer:
    """L3 状态层管理类"""

    def __init__(self, novel_path: str):
        self.novel_path = novel_path
        self.state_file = os.path.join(novel_path, ".novel", "state.json")
        self._state: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """从文件加载状态"""
        if os.path.exists(self.state_file):
            with open(self.state_file, "r", encoding="utf-8") as f:
                self._state = json.load(f)
        else:
            self._state = self._create_default_state()
            self._save()

    def _create_default_state(self) -> Dict[str, Any]:
        """创建默认状态结构"""
        return {
            "project_name": os.path.basename(self.novel_path),
            "current_chapter": 1,
            "drafts": {},
            "conversation_history": [],
            "story_state": {
                "timeline": {
                    "current_date": "初始",
                    "events": []
                },
                "character_status": {},
                "pending_foreshadowing": []
            }
        }

    def _save(self) -> None:
        """保存状态到文件"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self._state, f, ensure_ascii=False, indent=2)

    def get_state(self) -> Dict[str, Any]:
        """获取完整状态"""
        return self._state.copy()

    def _ensure_story_state(self) -> None:
        """确保 story_state 结构存在"""
        if "story_state" not in self._state:
            self._state["story_state"] = {
                "timeline": {"current_date": "初始", "events": []},
                "character_status": {},
                "pending_foreshadowing": []
            }

    def get_timeline(self) -> Dict[str, Any]:
        """获取时间线"""
        self._ensure_story_state()
        return self._state["story_state"]["timeline"].copy()

    def add_event(self, date: str, event: str) -> None:
        """添加事件到时间线

        Args:
            date: 事件日期
            event: 事件描述
        """
        self._ensure_story_state()
        timeline = self._state["story_state"]["timeline"]
        if "events" not in timeline:
            timeline["events"] = []
        timeline["events"].append({"date": date, "event": event})
        timeline["current_date"] = date
        self._save()

    def update_current_date(self, date: str) -> None:
        """更新当前日期"""
        self._ensure_story_state()
        self._state["story_state"]["timeline"]["current_date"] = date
        self._save()

    def get_character_status(self, name: str) -> Optional[Dict[str, Any]]:
        """获取角色状态"""
        self._ensure_story_state()
        character_status = self._state["story_state"]["character_status"]
        return character_status.get(name, None)

    def update_character_status(self, name: str, **kwargs) -> None:
        """更新角色状态

        Args:
            name: 角色名
            **kwargs: 要更新的字段，如 location, condition, inventory
        """
        self._ensure_story_state()
        character_status = self._state["story_state"]["character_status"]

        if name not in character_status:
            character_status[name] = {
                "location": "未知",
                "condition": "正常",
                "inventory": []
            }

        for key, value in kwargs.items():
            if key == "inventory" and isinstance(value, list):
                character_status[name]["inventory"] = value
            elif key in ["location", "condition"]:
                character_status[name][key] = value
            else:
                character_status[name][key] = value

        self._save()

    def add_item_to_character(self, name: str, item: str) -> None:
        """给角色添加物品"""
        self._ensure_story_state()
        character_status = self._state["story_state"]["character_status"]

        if name not in character_status:
            character_status[name] = {
                "location": "未知",
                "condition": "正常",
                "inventory": []
            }

        if "inventory" not in character_status[name]:
            character_status[name]["inventory"] = []

        if item not in character_status[name]["inventory"]:
            character_status[name]["inventory"].append(item)
            self._save()

    def remove_item_from_character(self, name: str, item: str) -> bool:
        """从角色移除物品"""
        self._ensure_story_state()
        character_status = self._state["story_state"]["character_status"]

        if name not in character_status or "inventory" not in character_status[name]:
            return False

        if item in character_status[name]["inventory"]:
            character_status[name]["inventory"].remove(item)
            self._save()
            return True
        return False

    def get_all_character_statuses(self) -> Dict[str, Dict[str, Any]]:
        """获取所有角色状态"""
        self._ensure_story_state()
        return self._state["story_state"]["character_status"].copy()

    def add_foreshadowing(self, id: str, hint: str) -> None:
        """添加未回收伏笔

        Args:
            id: 伏笔标识
            hint: 伏笔提示
        """
        self._ensure_story_state()
        pending = self._state["story_state"]["pending_foreshadowing"]

        for fs in pending:
            if fs["id"] == id:
                return

        pending.append({"id": id, "status": "unresolved", "hint": hint})
        self._save()

    def resolve_foreshadowing(self, id: str) -> bool:
        """标记伏笔已回收

        Args:
            id: 伏笔标识

        Returns:
            True if found and resolved, False if not found
        """
        self._ensure_story_state()
        pending = self._state["story_state"]["pending_foreshadowing"]

        for fs in pending:
            if fs["id"] == id:
                fs["status"] = "resolved"
                self._save()
                return True
        return False

    def get_pending_foreshadowing(self) -> List[Dict[str, str]]:
        """获取未回收伏笔列表"""
        self._ensure_story_state()
        pending = self._state["story_state"]["pending_foreshadowing"]
        return [fs for fs in pending if fs.get("status") == "unresolved"]

    def get_all_foreshadowing(self) -> List[Dict[str, str]]:
        """获取所有伏笔（包括已回收）"""
        self._ensure_story_state()
        return self._state["story_state"]["pending_foreshadowing"].copy()

    def update_draft(self, chapter: int, draft_content: str) -> None:
        """更新草稿

        Args:
            chapter: 章节号
            draft_content: 草稿内容
        """
        if "drafts" not in self._state:
            self._state["drafts"] = {}
        self._state["drafts"][str(chapter)] = draft_content
        self._save()

    def get_draft(self, chapter: int) -> Optional[str]:
        """获取草稿"""
        return self._state.get("drafts", {}).get(str(chapter), None)

    def set_current_chapter(self, chapter: int) -> None:
        """设置当前章节"""
        self._state["current_chapter"] = chapter
        self._save()

    def get_current_chapter(self) -> int:
        """获取当前章节"""
        return self._state.get("current_chapter", 1)
