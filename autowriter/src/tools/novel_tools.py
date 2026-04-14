"""写作辅助工具集

提供 expand_outline、update_timeline、check_foreshadowing、add_foreshadowing、
resolve_foreshadowing、get_character_status、update_character_status 等工具函数。
"""

import os
from typing import Dict, Any, List, Optional

from autowriter.src.tools.state_manager import StoryStateManager
from autowriter.src.llm.client import LLMClient


class NovelTools:
    """小说写作辅助工具集"""

    def __init__(self, novel_path: str):
        self.novel_path = novel_path
        self.state_file = os.path.join(novel_path, ".novel", "state.json")
        self.state_manager = StoryStateManager(self.state_file)
        self.llm_client = LLMClient()

    def expand_outline(self, idea: str, style: str = "detailed") -> str:
        """将粗略想法扩展为场景级大纲

        当用户只给出粗略想法（如一句话梗概），需要将其扩展为包含场景、冲突、角色的详细大纲时使用。
        可用于章节规划或片段构思。

        Args:
            idea: 用户提供的粗略想法或一句话梗概
            style: 大纲详细程度，'detailed' 或 'simple'，默认 'detailed'

        Returns:
            包含场景结构、冲突点、角色安排的大纲文本
        """
        from autowriter.src.memory import MemoryRetriever
        retriever = MemoryRetriever(self.novel_path)
        memory_context = retriever.get_full_index()

        prompt = f"""你是专业的小说大纲设计师。

【项目记忆索引】
{memory_context}

【当前时间线】
{self.state_manager.get_timeline()}

请将以下想法扩展为{"详细" if style == "detailed" else "简略"}的大纲：

{idea}

"""

        if style == "detailed":
            prompt += """大纲要求：
1. 场景设计：2-3个具体场景，包括场景描述
2. 冲突点：明确本章的核心冲突
3. 角色安排：涉及哪些角色，各自的行动
4. 伏笔提示：是否需要埋设伏笔

请直接输出大纲内容："""
        else:
            prompt += """请输出简要大纲（3-5行）："""

        try:
            if self.llm_client.config.api_key:
                response = self.llm_client.call(prompt, temperature=0.7, max_tokens=1500)
                return response.content or "[LLM 返回空内容]"
        except Exception:
            pass

        return f"""[模拟大纲输出]

场景一：开场
- 地点：苍云镇集市
- 人物：林清瑶
- 描写：清晨集市热闹，林清瑶在人群中穿行

场景二：发现线索
- 关键事件：林清瑶在角落发现可疑痕迹
- 伏笔：此处可埋下"神秘玉佩"伏笔

场景三：冲突升级
- 冲突：林清瑶被不明人物盯上
- 悬念：此人是谁？与灭门案有何关联？"""

    def update_timeline(
        self,
        action: str,
        event: Optional[str] = None,
        new_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """记录故事中发生的关键事件，或推进当前时间

        每次完成一段涉及时间推移的写作后应调用此工具，以保持时间线连贯。

        Args:
            action: 操作类型，'add_event' 或 'advance_date'
            event: 当 action=add_event 时，描述事件内容
            new_date: 当 action=advance_date 时，新的当前日期（如'三月十六'）

        Returns:
            操作结果，包含 success 和 timeline 信息
        """
        if action == "advance_date":
            if not new_date:
                return {
                    "success": False,
                    "error": "advance_date 操作需要提供 new_date 参数"
                }
            self.state_manager.advance_date(new_date)
            return {
                "success": True,
                "message": f"日期已推进到：{new_date}",
                "current_date": self.state_manager.get_current_date()
            }

        elif action == "add_event":
            if not event:
                return {
                    "success": False,
                    "error": "add_event 操作需要提供 event 参数"
                }
            self.state_manager.add_event(event)
            return {
                "success": True,
                "message": f"事件已添加：{event}",
                "current_date": self.state_manager.get_current_date(),
                "timeline": self.state_manager.get_timeline()
            }

        else:
            return {
                "success": False,
                "error": f"未知操作类型：{action}，支持 add_event 或 advance_date"
            }

    def check_foreshadowing(self) -> List[Dict[str, str]]:
        """查询当前故事中所有未回收的伏笔

        在开始新章节写作前或构思情节时使用，确保不遗忘已埋下的线索。

        Returns:
            未回收伏笔列表，每个包含 id、description、hint
        """
        return self.state_manager.get_pending_foreshadowing()

    def add_foreshadowing(self, description: str, hint: str = "") -> Dict[str, Any]:
        """在故事中埋下新伏笔

        伏笔是未来会揭晓的悬念或线索。

        Args:
            description: 伏笔的具体描述
            hint: 关于何时或如何回收的提示（可选）

        Returns:
            包含 success 和伏笔 ID
        """
        fs_id = self.state_manager.add_foreshadowing(description, hint)
        return {
            "success": True,
            "foreshadowing_id": fs_id,
            "message": f"伏笔已添加：{description}"
        }

    def resolve_foreshadowing(self, foreshadowing_id: str) -> Dict[str, Any]:
        """当某个伏笔被揭晓或回收时调用，标记为已解决

        Args:
            foreshadowing_id: 伏笔的唯一标识

        Returns:
            操作结果
        """
        success = self.state_manager.resolve_foreshadowing(foreshadowing_id)
        if success:
            return {
                "success": True,
                "message": f"伏笔 {foreshadowing_id} 已标记为已回收"
            }
        else:
            return {
                "success": False,
                "error": f"未找到伏笔：{foreshadowing_id}"
            }

    def get_character_status(self, character_name: str) -> Dict[str, Any]:
        """查询某个角色当前的位置、身体状况、携带物品等动态状态

        在描写角色出场前使用。

        Args:
            character_name: 角色名称

        Returns:
            角色的位置、身体状况、携带物品等状态信息
        """
        status = self.state_manager.get_character_status(character_name)
        if not status:
            return {
                "character_name": character_name,
                "status": "未记录",
                "message": f"角色 {character_name} 的状态尚未记录"
            }
        return {
            "character_name": character_name,
            "status": "已记录",
            **status
        }

    def update_character_status(
        self,
        character_name: str,
        location: Optional[str] = None,
        condition: Optional[str] = None,
        inventory_add: Optional[List[str]] = None,
        inventory_remove: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """更新角色的动态状态

        如移动到新地点、受伤、获得物品等。章节中角色状态变化后应调用。

        Args:
            character_name: 角色名称
            location: 新位置（可选）
            condition: 身体状况（可选）
            inventory_add: 新增物品列表（可选）
            inventory_remove: 移除物品列表（可选）

        Returns:
            操作结果
        """
        updates = {}
        if location is not None:
            updates["location"] = location
        if condition is not None:
            updates["condition"] = condition
        if inventory_add is not None:
            updates["inventory_add"] = inventory_add
        if inventory_remove is not None:
            updates["inventory_remove"] = inventory_remove

        if not updates:
            return {
                "success": False,
                "error": "未提供任何更新内容"
            }

        self.state_manager.update_character_status(character_name, **updates)

        return {
            "success": True,
            "message": f"角色 {character_name} 的状态已更新",
            "new_status": self.state_manager.get_character_status(character_name)
        }


def create_tools(novel_path: str) -> NovelTools:
    """工厂函数：创建工具实例"""
    return NovelTools(novel_path)
