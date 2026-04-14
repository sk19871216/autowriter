# 阶段三：工具化扩展规格文档

## Why

长篇创作需要更高级的规划能力、时间线管理和伏笔追踪功能。目前系统已经能够"记住"角色、世界观，并在写作时检索。但缺少主动规划、状态追踪和工具协作能力。

第三步的目标是：将这些能力封装为独立的工具，让 Agent 像 Claude Code 一样，能够自主决策、组合调用它们，实现从"被动响应"到"主动规划"的升级。

## What Changes

### 1. 新增工具清单

| 工具名称 | 功能 | 触发场景 |
|---------|------|---------|
| `expand_outline` | 将一句话梗概扩展为场景级大纲 | 用户给出粗略想法，需要细化结构 |
| `update_timeline` | 在时间线上记录事件或推进日期 | 章节涉及时间推移或关键事件发生 |
| `check_foreshadowing` | 查询未回收的伏笔列表 | 写作前或写作后，提醒埋坑/回收 |
| `add_foreshadowing` | 记录一个新伏笔 | 章节中埋下伏笔时自动或手动调用 |
| `resolve_foreshadowing` | 标记某个伏笔已回收 | 伏笔被揭晓时 |
| `get_character_status` | 查询角色当前状态（位置、伤势、物品） | 需要知道角色"此刻"在哪里、有什么 |
| `update_character_status` | 更新角色状态 | 章节中角色移动、受伤、获得物品时 |

### 2. StoryStateManager 核心类

新增 `StoryStateManager` 类，专门处理 `state.json` 中的 `story_state` 部分：

```python
class StoryStateManager:
    # --- 时间线操作 ---
    def get_current_date(self) -> str
    def advance_date(self, new_date: str)
    def add_event(self, event_description: str, date: str = None)

    # --- 伏笔操作 ---
    def get_pending_foreshadowing(self) -> List[Dict]
    def add_foreshadowing(self, description: str, hint: str = "") -> str
    def resolve_foreshadowing(self, fs_id: str) -> bool

    # --- 角色状态操作 ---
    def get_character_status(self, name: str) -> Dict
    def update_character_status(self, name: str, **kwargs)
```

### 3. 工具描述设计规范

每个工具的描述必须包含：
- **功能说明**：工具能做什么
- **触发条件**：何时该用
- **输入参数格式**：参数类型和说明
- **返回值格式**：返回值的结构和含义

### 4. Agent 决策流程扩展

Agent 在处理复杂任务时，可自主决策调用工具链：

```
用户输入 → expand_outline(扩展大纲) → query_memory(查询背景) → 
check_foreshadowing(检查伏笔) → write_draft(写作) → 
update_timeline(更新时间线) → add_foreshadowing(如有新伏笔) → finish
```

## Impact

- **Affected specs**：
  - `phase-2-memory/spec.md` - 工具将调用现有的 StateLayer/IndexLayer
  - `novel-assistant-master/spec.md` - 工具集扩展

- **Affected code**：
  - `autowriter/src/tools/state_manager.py` - 新增 StoryStateManager 类
  - `autowriter/src/tools/__init__.py` - 新增工具导出
  - `autowriter/src/core/agent.py` - 新增工具处理方法

## ADDED Requirements

### Requirement: expand_outline 工具

系统 SHALL 提供 `expand_outline` 工具将用户粗略想法扩展为详细大纲。

**参数**：
- `idea` (string, required): 用户提供的粗略想法或一句话梗概
- `style` (string, optional): 大纲详细程度，`detailed` 或 `simple`，默认 `detailed`

**触发条件**：当用户只给出粗略想法，需要将其扩展为包含场景、冲突、角色的详细大纲时使用。

**返回**：包含场景结构、冲突点、角色安排的大纲文本。

### Requirement: update_timeline 工具

系统 SHALL 提供 `update_timeline` 工具管理时间线。

**参数**：
- `action` (string, required): 操作类型，`add_event` 或 `advance_date`
- `event` (string, optional): 当 action=add_event 时，描述事件内容
- `new_date` (string, optional): 当 action=advance_date 时，新的当前日期

**触发条件**：每次完成一段涉及时间推移的写作后应调用此工具，以保持时间线连贯。

### Requirement: check_foreshadowing 工具

系统 SHALL 提供 `check_foreshadowing` 工具查询未回收伏笔。

**参数**：无

**触发条件**：在开始新章节写作前或构思情节时使用，确保不遗忘已埋下的线索。

**返回**：当前故事中所有未回收的伏笔列表，每个包含 id、description、hint。

### Requirement: add_foreshadowing 工具

系统 SHALL 提供 `add_foreshadowing` 工具记录新伏笔。

**参数**：
- `description` (string, required): 伏笔的具体描述
- `hint` (string, optional): 关于何时或如何回收的提示

**触发条件**：在故事中埋下新伏笔时调用。伏笔是未来会揭晓的悬念或线索。

**返回**：新创建的伏笔唯一标识 ID。

### Requirement: resolve_foreshadowing 工具

系统 SHALL 提供 `resolve_foreshadowing` 工具标记伏笔已回收。

**参数**：
- `foreshadowing_id` (string, required): 伏笔的唯一标识

**触发条件**：当某个伏笔被揭晓或回收时调用，标记为已解决。

**返回**：操作是否成功。

### Requirement: get_character_status 工具

系统 SHALL 提供 `get_character_status` 工具查询角色动态状态。

**参数**：
- `character_name` (string, required): 角色名称

**触发条件**：查询某个角色当前的位置、身体状况、携带物品等动态状态。在描写角色出场前使用。

**返回**：角色的位置、身体状况、携带物品等状态信息。

### Requirement: update_character_status 工具

系统 SHALL 提供 `update_character_status` 工具更新角色状态。

**参数**：
- `character_name` (string, required): 角色名称
- `location` (string, optional): 新位置
- `condition` (string, optional): 身体状况
- `inventory_add` (array, optional): 新增物品列表
- `inventory_remove` (array, optional): 移除物品列表

**触发条件**：章节中角色状态变化后应调用，如移动到新地点、受伤、获得物品等。

## MODIFIED Requirements

### Requirement: StoryStateManager 与 StateLayer 整合

**原有**：`StateLayer` 类管理 state.json 的读写

**扩展后**：
- 新增 `StoryStateManager` 类作为高级封装
- StoryStateManager 组合调用 StateLayer 的基础方法
- 提供更友好的工具接口

## 代码模块清单

| 文件 | 修改/新增内容 |
|------|--------------|
| `autowriter/src/tools/state_manager.py` | 新增 StoryStateManager 类 |
| `autowriter/src/tools/__init__.py` | 导出新工具函数 |
| `autowriter/src/core/agent.py` | 新增工具处理方法（expand_outline、update_timeline 等） |
| `autowriter/src/core/react.py` | 扩展工具定义列表 |

## 工具定义示例

### expand_outline

```json
{
  "type": "function",
  "function": {
    "name": "expand_outline",
    "description": "当用户只给出粗略想法（如一句话梗概），需要将其扩展为包含场景、冲突、角色的详细大纲时使用。可用于章节规划或片段构思。",
    "parameters": {
      "type": "object",
      "properties": {
        "idea": {
          "type": "string",
          "description": "用户提供的粗略想法或一句话梗概"
        },
        "style": {
          "type": "string",
          "enum": ["detailed", "simple"],
          "description": "大纲详细程度，默认为 detailed"
        }
      },
      "required": ["idea"]
    }
  }
}
```

### update_timeline

```json
{
  "type": "function",
  "function": {
    "name": "update_timeline",
    "description": "记录故事中发生的关键事件，或推进当前时间。每次完成一段涉及时间推移的写作后应调用此工具，以保持时间线连贯。",
    "parameters": {
      "type": "object",
      "properties": {
        "action": {
          "type": "string",
          "enum": ["add_event", "advance_date"],
          "description": "操作类型：添加事件或推进日期"
        },
        "event": {
          "type": "string",
          "description": "当 action=add_event 时，描述事件内容"
        },
        "new_date": {
          "type": "string",
          "description": "当 action=advance_date 时，新的当前日期（如'三月十六'）"
        }
      },
      "required": ["action"]
    }
  }
}
```

### check_foreshadowing / add_foreshadowing / resolve_foreshadowing

```json
{
  "name": "check_foreshadowing",
  "description": "查询当前故事中所有未回收的伏笔。在开始新章节写作前或构思情节时使用，确保不遗忘已埋下的线索。",
  "parameters": { "type": "object", "properties": {} }
},
{
  "name": "add_foreshadowing",
  "description": "在故事中埋下新伏笔时调用。伏笔是未来会揭晓的悬念或线索。",
  "parameters": {
    "type": "object",
    "properties": {
      "description": { "type": "string", "description": "伏笔的具体描述" },
      "hint": { "type": "string", "description": "关于何时或如何回收的提示（可选）" }
    },
    "required": ["description"]
  }
},
{
  "name": "resolve_foreshadowing",
  "description": "当某个伏笔被揭晓或回收时调用，标记为已解决。",
  "parameters": {
    "type": "object",
    "properties": {
      "foreshadowing_id": { "type": "string", "description": "伏笔的唯一标识（由系统在添加时返回）" }
    },
    "required": ["foreshadowing_id"]
  }
}
```

### get_character_status / update_character_status

```json
{
  "name": "get_character_status",
  "description": "查询某个角色当前的位置、身体状况、携带物品等动态状态。在描写角色出场前使用。",
  "parameters": {
    "type": "object",
    "properties": {
      "character_name": { "type": "string" }
    },
    "required": ["character_name"]
  }
},
{
  "name": "update_character_status",
  "description": "更新角色的动态状态，如移动到新地点、受伤、获得物品等。章节中角色状态变化后应调用。",
  "parameters": {
    "type": "object",
    "properties": {
      "character_name": { "type": "string" },
      "location": { "type": "string", "description": "新位置（可选）" },
      "condition": { "type": "string", "description": "身体状况（可选）" },
      "inventory_add": { "type": "array", "items": { "type": "string" }, "description": "新增物品（可选）" },
      "inventory_remove": { "type": "array", "items": { "type": "string" }, "description": "移除物品（可选）" }
    },
    "required": ["character_name"]
  }
}
```

## Agent 决策流程示例

**用户输入**：
```
📖 > 构思第三章：林清瑶在苍云镇集市发现灭门案线索。
```

**Agent 内部推理链**：
1. 调用 `expand_outline`：将用户想法扩展为详细场景大纲
2. 调用 `query_memory`：查询"苍云镇"、"灭门案"已有设定
3. 调用 `check_foreshadowing`：查看当前未回收伏笔，思考能否关联
4. 调用 `write_draft`：根据大纲和背景信息写出草稿
5. （写作后）调用 `update_timeline`：记录事件发生日期
6. （如有新伏笔）调用 `add_foreshadowing`：记录"集市上神秘人留下的玉佩"
7. 调用 `finish_task`：报告完成

整个过程由 Agent 自主决策，用户只需给出高层指令。
