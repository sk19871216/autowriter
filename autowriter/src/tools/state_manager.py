"""StoryStateManager - 状态管理工具

专门处理 state.json 中的 story_state 部分，提供高级封装的操作接口。
"""

import json
import os
import uuid
from typing import Dict, List, Optional, Any


class StoryStateManager:
    """故事状态管理器

    封装 state.json 中 story_state 部分的读写操作，
    提供时间线、伏笔、角色状态的高级管理接口。
    """

    def __init__(self, state_file_path: str):
        self.state_file = state_file_path
        self.state: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """从文件加载状态"""
        if os.path.exists(self.state_file):
            with open(self.state_file, "r", encoding="utf-8") as f:
                self.state = json.load(f)
        else:
            self.state = self._create_default_state()
            self._save()

    def _create_default_state(self) -> Dict[str, Any]:
        """创建默认状态结构"""
        return {
            "project_name": os.path.basename(os.path.dirname(self.state_file)),
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
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def _ensure_story_state(self) -> None:
        """确保 story_state 结构存在"""
        if "story_state" not in self.state:
            self.state["story_state"] = {
                "timeline": {"current_date": "初始", "events": []},
                "character_status": {},
                "pending_foreshadowing": []
            }

    def get_current_date(self) -> str:
        """获取当前日期

        Returns:
            当前日期字符串
        """
        self._ensure_story_state()
        return self.state["story_state"]["timeline"]["current_date"]

    def advance_date(self, new_date: str) -> None:
        """推进日期

        Args:
            new_date: 新的当前日期（如'三月十六'）
        """
        self._ensure_story_state()
        self.state["story_state"]["timeline"]["current_date"] = new_date
        self._save()

    def add_event(self, event_description: str, date: str = None) -> None:
        """添加事件到时间线

        Args:
            event_description: 事件描述
            date: 事件日期，默认为当前日期
        """
        self._ensure_story_state()
        date = date or self.get_current_date()

        if "events" not in self.state["story_state"]["timeline"]:
            self.state["story_state"]["timeline"]["events"] = []

        self.state["story_state"]["timeline"]["events"].append({
            "date": date,
            "event": event_description
        })
        self.state["story_state"]["timeline"]["current_date"] = date
        self._save()

    def get_timeline(self) -> Dict[str, Any]:
        """获取完整时间线

        Returns:
            包含 current_date 和 events 的时间线字典
        """
        self._ensure_story_state()
        return self.state["story_state"]["timeline"].copy()

    def get_pending_foreshadowing(self) -> List[Dict[str, str]]:
        """获取未回收的伏笔列表

        Returns:
            未回收伏笔的列表，每个包含 id、description、hint
        """
        self._ensure_story_state()
        pending = self.state["story_state"]["pending_foreshadowing"]
        return [
            fs for fs in pending
            if fs.get("status") == "unresolved"
        ]

    def add_foreshadowing(self, description: str, hint: str = "") -> str:
        """添加新伏笔

        Args:
            description: 伏笔的具体描述
            hint: 关于何时或如何回收的提示（可选）

        Returns:
            新创建的伏笔唯一标识 ID
        """
        self._ensure_story_state()

        fs_id = str(uuid.uuid4())[:8]

        if "pending_foreshadowing" not in self.state["story_state"]:
            self.state["story_state"]["pending_foreshadowing"] = []

        self.state["story_state"]["pending_foreshadowing"].append({
            "id": fs_id,
            "description": description,
            "hint": hint,
            "status": "unresolved"
        })
        self._save()
        return fs_id

    def resolve_foreshadowing(self, fs_id: str) -> bool:
        """标记伏笔已回收

        Args:
            fs_id: 伏笔的唯一标识

        Returns:
            操作是否成功（True 找到并标记，False 未找到）
        """
        self._ensure_story_state()
        pending = self.state["story_state"]["pending_foreshadowing"]

        for fs in pending:
            if fs["id"] == fs_id:
                fs["status"] = "resolved"
                self._save()
                return True
        return False

    def get_all_foreshadowing(self) -> List[Dict[str, str]]:
        """获取所有伏笔（包括已回收和未回收）

        Returns:
            所有伏笔的列表
        """
        self._ensure_story_state()
        return self.state["story_state"]["pending_foreshadowing"].copy()

    def get_character_status(self, name: str) -> Dict[str, Any]:
        """获取角色状态

        Args:
            name: 角色名称

        Returns:
            角色的位置、身体状况、携带物品等状态信息
        """
        self._ensure_story_state()
        return self.state["story_state"]["character_status"].get(name, {})

    def update_character_status(self, name: str, **kwargs) -> None:
        """更新角色状态

        Args:
            name: 角色名称
            **kwargs: 要更新的字段
                - location: 新位置
                - condition: 身体状况
                - inventory_add: 新增物品列表
                - inventory_remove: 移除物品列表
        """
        self._ensure_story_state()

        if name not in self.state["story_state"]["character_status"]:
            self.state["story_state"]["character_status"][name] = {}

        char = self.state["story_state"]["character_status"][name]

        for key, value in kwargs.items():
            if key == "inventory_add":
                char.setdefault("inventory", []).extend(value)
            elif key == "inventory_remove":
                if "inventory" in char:
                    char["inventory"] = [i for i in char["inventory"] if i not in value]
            else:
                char[key] = value

        self._save()

    def get_all_character_statuses(self) -> Dict[str, Dict[str, Any]]:
        """获取所有角色状态

        Returns:
            所有角色状态的字典
        """
        self._ensure_story_state()
        return self.state["story_state"]["character_status"].copy()
