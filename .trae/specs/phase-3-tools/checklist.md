# 检查清单 - 阶段三：工具化扩展

本文档用于验证阶段三实现是否满足规格要求。

---

## StoryStateManager 类检查

- [x] `StoryStateManager` 类已创建在 `autowriter/src/tools/state_manager.py` ✅
- [x] `__init__(self, state_file_path)` 方法实现 ✅
- [x] `_load()` 私有方法实现 ✅
- [x] `_save()` 私有方法实现 ✅

### 时间线操作方法

- [x] `get_current_date()` 方法实现 ✅
- [x] `advance_date(new_date)` 方法实现 ✅
- [x] `add_event(event_description, date=None)` 方法实现 ✅

### 伏笔操作方法

- [x] `get_pending_foreshadowing()` 方法实现 ✅
- [x] `add_foreshadowing(description, hint="")` 方法实现，返回伏笔 ID ✅
- [x] `resolve_foreshadowing(fs_id)` 方法实现 ✅

### 角色状态操作方法

- [x] `get_character_status(name)` 方法实现 ✅
- [x] `update_character_status(name, **kwargs)` 方法实现 ✅
- [x] 支持 `location` 参数 ✅
- [x] 支持 `condition` 参数 ✅
- [x] 支持 `inventory_add` 参数 ✅
- [x] 支持 `inventory_remove` 参数 ✅

---

## 工具结构定义检查

### expand_outline 工具

- [x] 工具名称为 `expand_outline` ✅
- [x] 描述包含功能说明 ✅
- [x] 描述包含触发条件 ✅
- [x] 参数 `idea` (string, required) 定义 ✅
- [x] 参数 `style` (string, optional) 定义，enum: ["detailed", "simple"] ✅

### update_timeline 工具

- [x] 工具名称为 `update_timeline` ✅
- [x] 描述包含功能说明 ✅
- [x] 描述包含触发条件 ✅
- [x] 参数 `action` (string, required), enum: ["add_event", "advance_date"] ✅
- [x] 参数 `event` (string, optional) 定义 ✅
- [x] 参数 `new_date` (string, optional) 定义 ✅

### check_foreshadowing 工具

- [x] 工具名称为 `check_foreshadowing` ✅
- [x] 描述包含功能说明 ✅
- [x] 描述包含触发条件 ✅
- [x] 参数为空对象 ✅

### add_foreshadowing 工具

- [x] 工具名称为 `add_foreshadowing` ✅
- [x] 描述包含功能说明 ✅
- [x] 描述包含触发条件 ✅
- [x] 参数 `description` (string, required) 定义 ✅
- [x] 参数 `hint` (string, optional) 定义 ✅

### resolve_foreshadowing 工具

- [x] 工具名称为 `resolve_foreshadowing` ✅
- [x] 描述包含功能说明 ✅
- [x] 描述包含触发条件 ✅
- [x] 参数 `foreshadowing_id` (string, required) 定义 ✅

### get_character_status 工具

- [x] 工具名称为 `get_character_status` ✅
- [x] 描述包含功能说明 ✅
- [x] 描述包含触发条件 ✅
- [x] 参数 `character_name` (string, required) 定义 ✅

### update_character_status 工具

- [x] 工具名称为 `update_character_status` ✅
- [x] 描述包含功能说明 ✅
- [x] 描述包含触发条件 ✅
- [x] 参数 `character_name` (string, required) 定义 ✅
- [x] 参数 `location` (string, optional) 定义 ✅
- [x] 参数 `condition` (string, optional) 定义 ✅
- [x] 参数 `inventory_add` (array, optional) 定义 ✅
- [x] 参数 `inventory_remove` (array, optional) 定义 ✅

---

## 工具函数实现检查

### 工具文件结构

- [x] `autowriter/src/tools/state_manager.py` 存在 ✅
- [x] `autowriter/src/tools/novel_tools.py` 存在 ✅
- [x] `autowriter/src/tools/__init__.py` 已更新导出新工具 ✅

### expand_outline 函数

- [x] 函数 `expand_outline(idea, style="detailed")` 实现 ✅
- [x] 调用 LLM 生成大纲 ✅
- [x] 返回格式化的场景级大纲 ✅

### update_timeline 函数

- [x] 函数 `update_timeline(action, event=None, new_date=None)` 实现 ✅
- [x] 调用 StoryStateManager 的相应方法 ✅
- [x] 返回操作结果 ✅

### 伏笔工具函数

- [x] 函数 `check_foreshadowing()` 实现 ✅
- [x] 函数 `add_foreshadowing(description, hint="")` 实现 ✅
- [x] 函数 `resolve_foreshadowing(foreshadowing_id)` 实现 ✅
- [x] 各函数正确调用 StoryStateManager 方法 ✅

### 角色状态工具函数

- [x] 函数 `get_character_status(character_name)` 实现 ✅
- [x] 函数 `update_character_status(character_name, **kwargs)` 实现 ✅
- [x] 各函数正确调用 StoryStateManager 方法 ✅

---

## Agent 集成检查

### agent.py 更新

- [x] 新工具已添加到工具定义列表 ✅
- [x] 工具描述完整准确 ✅

### Agent 处理方法

- [x] `_tool_expand_outline` 方法实现 ✅
- [x] `_tool_update_timeline` 方法实现 ✅
- [x] `_tool_check_foreshadowing` 方法实现 ✅
- [x] `_tool_add_foreshadowing` 方法实现 ✅
- [x] `_tool_resolve_foreshadowing` 方法实现 ✅
- [x] `_tool_get_character_status` 方法实现 ✅
- [x] `_tool_update_character_status` 方法实现 ✅

### 决策流程提示

- [x] System prompt 包含工具使用提示 ✅
- [x] 提示在写作前使用 check_foreshadowing ✅
- [x] 提示在写作后使用 update_timeline ✅

---

## 单元测试检查

### StoryStateManager 测试

- [x] 测试文件 `tests/test_tools.py` 存在 ✅
- [x] 测试 `get_current_date` 和 `advance_date` ✅
- [x] 测试 `add_event` ✅
- [x] 测试 `add_foreshadowing` 和 `get_pending_foreshadowing` ✅
- [x] 测试 `resolve_foreshadowing` ✅
- [x] 测试 `get_character_status` 和 `update_character_status` ✅

### 工具函数测试

- [x] 测试 `expand_outline` 输出格式 ✅
- [x] 测试 `update_timeline` 返回值 ✅
- [x] 测试伏笔工具的 ID 生成和状态更新 ✅
- [x] 测试角色状态工具的物品管理 ✅

### 测试结果

- [x] 28 个测试全部通过 ✅

---

## 集成验证检查

### 场景：构思第三章

- [x] 用户输入粗略想法后，Agent 能调用 expand_outline 生成大纲
- [x] Agent 能调用 check_foreshadowing 查看未回收伏笔
- [x] 写作后 Agent 能调用 update_timeline 更新时间线
- [x] 如有新伏笔，Agent 能调用 add_foreshadowing 记录

### 场景：角色状态管理

- [x] 用户询问角色状态时，Agent 能调用 get_character_status
- [x] 角色移动后，Agent 能调用 update_character_status 更新位置
- [x] 角色获得物品后，inventory_add 能正确添加物品
- [x] 角色失去物品后，inventory_remove 能正确移除物品

---

## 阶段三验收状态

- [x] StoryStateManager 类实现完成 ✅
- [x] 所有工具结构定义完整 ✅
- [x] 工具函数实现正确 ✅
- [x] Agent 集成完成 ✅
- [x] 单元测试覆盖主要功能 ✅
- [x] 所有 28 个测试通过 ✅
