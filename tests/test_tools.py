"""阶段三工具测试：StoryStateManager 和 NovelTools"""

import os
import json
import tempfile
import shutil
from typing import Dict, Any, List

import pytest

from autowriter.src.tools.state_manager import StoryStateManager
from autowriter.src.tools.novel_tools import NovelTools


class TestStoryStateManager:
    """测试 StoryStateManager 类"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录用于测试"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def state_file(self, temp_dir):
        """创建临时 state.json 文件路径"""
        novel_dir = os.path.join(temp_dir, ".novel")
        os.makedirs(novel_dir, exist_ok=True)
        return os.path.join(novel_dir, "state.json")

    @pytest.fixture
    def manager(self, state_file):
        """创建 StoryStateManager 实例"""
        return StoryStateManager(state_file)

    def test_init_creates_default_state(self, state_file, manager):
        """测试初始化创建默认状态"""
        assert os.path.exists(state_file)
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
        assert "story_state" in state
        assert "timeline" in state["story_state"]
        assert "character_status" in state["story_state"]
        assert "pending_foreshadowing" in state["story_state"]

    def test_get_current_date(self, manager):
        """测试获取当前日期"""
        date = manager.get_current_date()
        assert date == "初始"

    def test_advance_date(self, manager):
        """测试推进日期"""
        manager.advance_date("三月十五")
        assert manager.get_current_date() == "三月十五"

    def test_add_event(self, manager):
        """测试添加事件"""
        manager.add_event("林清瑶抵达苍云镇", "三月初十")
        timeline = manager.get_timeline()
        assert len(timeline["events"]) == 1
        assert timeline["events"][0]["date"] == "三月初十"
        assert timeline["events"][0]["event"] == "林清瑶抵达苍云镇"
        assert timeline["current_date"] == "三月初十"

    def test_add_foreshadowing(self, manager):
        """测试添加伏笔"""
        fs_id = manager.add_foreshadowing("神秘玉佩", "第三章回收")
        assert fs_id is not None
        assert len(fs_id) == 8

        pending = manager.get_pending_foreshadowing()
        assert len(pending) == 1
        assert pending[0]["description"] == "神秘玉佩"
        assert pending[0]["hint"] == "第三章回收"
        assert pending[0]["status"] == "unresolved"

    def test_resolve_foreshadowing(self, manager):
        """测试回收伏笔"""
        fs_id = manager.add_foreshadowing("神秘玉佩", "")
        result = manager.resolve_foreshadowing(fs_id)
        assert result is True

        pending = manager.get_pending_foreshadowing()
        assert len(pending) == 0

        all_fs = manager.get_all_foreshadowing()
        assert len(all_fs) == 1
        assert all_fs[0]["status"] == "resolved"

    def test_resolve_nonexistent_foreshadowing(self, manager):
        """测试回收不存在的伏笔"""
        result = manager.resolve_foreshadowing("nonexistent_id")
        assert result is False

    def test_get_character_status_new(self, manager):
        """测试获取新角色状态"""
        status = manager.get_character_status("林清瑶")
        assert status == {}

    def test_update_character_status_location(self, manager):
        """测试更新角色位置"""
        manager.update_character_status("林清瑶", location="苍云镇集市")
        status = manager.get_character_status("林清瑶")
        assert status["location"] == "苍云镇集市"

    def test_update_character_status_condition(self, manager):
        """测试更新角色状态"""
        manager.update_character_status("林清瑶", condition="轻伤")
        status = manager.get_character_status("林清瑶")
        assert status["condition"] == "轻伤"

    def test_update_character_status_inventory_add(self, manager):
        """测试添加物品"""
        manager.update_character_status("林清瑶", inventory_add=["青云剑", "伤药"])
        status = manager.get_character_status("林清瑶")
        assert "青云剑" in status["inventory"]
        assert "伤药" in status["inventory"]

    def test_update_character_status_inventory_remove(self, manager):
        """测试移除物品"""
        manager.update_character_status("林清瑶", inventory_add=["青云剑", "伤药"])
        manager.update_character_status("林清瑶", inventory_remove=["伤药"])
        status = manager.get_character_status("林清瑶")
        assert "青云剑" in status["inventory"]
        assert "伤药" not in status["inventory"]

    def test_get_all_character_statuses(self, manager):
        """测试获取所有角色状态"""
        manager.update_character_status("林清瑶", location="苍云镇")
        manager.update_character_status("柳慕白", location="破庙")
        statuses = manager.get_all_character_statuses()
        assert "林清瑶" in statuses
        assert "柳慕白" in statuses


class TestNovelTools:
    """测试 NovelTools 类"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录用于测试"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def tools(self, temp_dir):
        """创建 NovelTools 实例"""
        novel_dir = os.path.join(temp_dir, "my_novel")
        os.makedirs(novel_dir, exist_ok=True)
        return NovelTools(novel_dir)

    def test_update_timeline_add_event(self, tools):
        """测试添加事件"""
        result = tools.update_timeline(action="add_event", event="林清瑶离开青云宗")
        assert result["success"] is True
        assert "林清瑶离开青云宗" in result["message"]

    def test_update_timeline_advance_date(self, tools):
        """测试推进日期"""
        result = tools.update_timeline(action="advance_date", new_date="三月十五")
        assert result["success"] is True
        assert result["current_date"] == "三月十五"

    def test_update_timeline_missing_params(self, tools):
        """测试缺少参数"""
        result = tools.update_timeline(action="advance_date")
        assert result["success"] is False
        assert "需要提供 new_date" in result["error"]

        result = tools.update_timeline(action="add_event")
        assert result["success"] is False
        assert "需要提供 event" in result["error"]

    def test_update_timeline_invalid_action(self, tools):
        """测试无效操作"""
        result = tools.update_timeline(action="invalid_action")
        assert result["success"] is False
        assert "未知操作类型" in result["error"]

    def test_check_foreshadowing_empty(self, tools):
        """测试检查伏笔（空列表）"""
        result = tools.check_foreshadowing()
        assert result == []

    def test_add_foreshadowing(self, tools):
        """测试添加伏笔"""
        result = tools.add_foreshadowing("神秘玉佩", "第三章回收")
        assert result["success"] is True
        assert "foreshadowing_id" in result
        assert len(result["foreshadowing_id"]) == 8

    def test_check_foreshadowing_after_add(self, tools):
        """测试添加后检查伏笔"""
        tools.add_foreshadowing("神秘玉佩", "")
        result = tools.check_foreshadowing()
        assert len(result) == 1
        assert result[0]["description"] == "神秘玉佩"

    def test_resolve_foreshadowing(self, tools):
        """测试回收伏笔"""
        add_result = tools.add_foreshadowing("神秘玉佩", "")
        fs_id = add_result["foreshadowing_id"]

        result = tools.resolve_foreshadowing(fs_id)
        assert result["success"] is True

        pending = tools.check_foreshadowing()
        assert len(pending) == 0

    def test_resolve_nonexistent_foreshadowing(self, tools):
        """测试回收不存在的伏笔"""
        result = tools.resolve_foreshadowing("nonexistent")
        assert result["success"] is False
        assert "未找到" in result["error"]

    def test_get_character_status_new(self, tools):
        """测试获取新角色状态"""
        result = tools.get_character_status("林清瑶")
        assert result["status"] == "未记录"

    def test_update_character_status(self, tools):
        """测试更新角色状态"""
        result = tools.update_character_status(
            character_name="林清瑶",
            location="苍云镇集市",
            condition="轻伤",
            inventory_add=["青云剑"]
        )
        assert result["success"] is True

        status = tools.get_character_status("林清瑶")
        assert status["status"] == "已记录"
        assert status["location"] == "苍云镇集市"
        assert status["condition"] == "轻伤"
        assert "青云剑" in status["inventory"]

    def test_update_character_status_no_params(self, tools):
        """测试更新角色状态但不提供参数"""
        result = tools.update_character_status(character_name="林清瑶")
        assert result["success"] is False
        assert "未提供任何更新内容" in result["error"]

    def test_expand_outline(self, tools):
        """测试扩展大纲"""
        result = tools.expand_outline("林清瑶在苍云镇集市发现灭门案线索", style="detailed")
        assert isinstance(result, str)
        assert len(result) > 0


class TestIntegration:
    """集成测试：测试工具链协作"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录用于测试"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def tools(self, temp_dir):
        """创建 NovelTools 实例"""
        novel_dir = os.path.join(temp_dir, "my_novel")
        os.makedirs(novel_dir, exist_ok=True)
        return NovelTools(novel_dir)

    def test_timeline_and_foreshadowing_workflow(self, tools):
        """测试时间线和伏笔工作流"""
        tools.update_timeline(action="advance_date", new_date="三月初十")

        tools.add_foreshadowing("神秘玉佩", "第三章在集市被发现")

        pending = tools.check_foreshadowing()
        assert len(pending) == 1
        assert pending[0]["description"] == "神秘玉佩"

        tools.update_timeline(action="add_event", event="林清瑶在集市发现玉佩")

        timeline = tools.state_manager.get_timeline()
        assert timeline["current_date"] == "三月初十"
        assert len(timeline["events"]) == 1

    def test_character_status_workflow(self, tools):
        """测试角色状态工作流"""
        tools.update_character_status(
            character_name="林清瑶",
            location="青云宗",
            condition="正常",
            inventory_add=["青云剑"]
        )

        tools.update_character_status(
            character_name="林清瑶",
            location="苍云镇",
            condition="轻伤",
            inventory_add=["神秘玉佩"]
        )

        status = tools.get_character_status("林清瑶")
        assert status["location"] == "苍云镇"
        assert status["condition"] == "轻伤"
        assert "青云剑" in status["inventory"]
        assert "神秘玉佩" in status["inventory"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
