# 任务列表 - 阶段二：分层记忆系统

本任务列表实现三层记忆模型的代码层。

---

## 任务 2.1: 实现 L1 索引层 (index_layer.py)

创建 `IndexLayer` 类管理 `memory_index.md` 的读写和检索。

- [x] 子任务 2.1.1: 创建 `IndexLayer` 类框架 ✅
  - 初始化时传入 `novel_path`（小说工程根目录）
  - 索引文件路径：`{novel_path}/.novel/memory_index.md`

- [x] 子任务 2.1.2: 实现 `add_entry(type, name, description, anchor)` 方法 ✅
  - 格式：`{type} {name} | {description} | {anchor}`
  - 验证每行不超过 150 字符
  - 按类型分类存储（char/world/event/foreshadow）

- [x] 子任务 2.1.3: 实现 `remove_entry(name)` 方法 ✅
  - 通过名称匹配删除条目
  - 支持精确匹配

- [x] 子任务 2.1.4: 实现 `search(query, top_k=3)` 方法 ✅
  - 计算每行与 query 的相似度（关键词重叠率）
  - 返回相似度最高的 top_k 个条目
  - 返回格式：`[(entry, score), ...]`

- [x] 子任务 2.1.5: 实现 `update_entry(name, **kwargs)` 方法 ✅
  - 根据 name 查找并更新条目
  - 支持更新 description

- [x] 子任务 2.1.6: 实现格式验证 ✅
  - 每行使用 `|` 分隔三个字段
  - 类型前缀为 `char`/`world`/`event`/`foreshadow`
  - 150 字符限制检查

---

## 任务 2.2: 实现 L2 详情层 (detail_layer.py)

创建 `DetailLayer` 类管理 `memories/*.md` 的读写。

- [x] 子任务 2.2.1: 创建 `DetailLayer` 类框架 ✅
  - 初始化时传入 `novel_path`
  - 详情目录路径：`{novel_path}/.novel/memories/`

- [x] 子任务 2.2.2: 实现 `get_detail(file, anchor)` 方法 ✅
  - 解析 `file#anchor` 格式
  - 读取 Markdown 文件
  - 提取锚点 `# 标题` 下的内容块
  - 返回该锚点下的所有内容直到下一个同/高级标题

- [x] 子任务 2.2.3: 实现 `update_detail(file, anchor, content)` 方法 ✅
  - 在指定锚点下更新内容
  - 若锚点不存在则创建

- [x] 子任务 2.2.4: 实现 `create_anchor(file, anchor, content)` 方法 ✅
  - 在指定文件末尾添加新锚点条目
  - 格式符合 Markdown 标题规范

- [x] 子任务 2.2.5: 标准化 memories/ 目录下的文件格式 ✅
  - `characters.md`: 角色档案
  - `worldview.md`: 世界观/地点
  - `timeline.md`: 时间线事件
  - `foreshadowing.md`: 伏笔

---

## 任务 2.3: 实现 L3 状态层 (state_layer.py)

创建 `StateLayer` 类管理 `state.json` 的读写和状态更新。

- [x] 子任务 2.3.1: 创建 `StateLayer` 类框架 ✅
  - 初始化时传入 `novel_path`
  - 状态文件路径：`{novel_path}/.novel/state.json`

- [x] 子任务 2.3.2: 实现 `story_state` 结构扩展 ✅
  - 设计 `timeline` 字段结构
  - 设计 `character_status` 字段结构
  - 设计 `pending_foreshadowing` 字段结构

- [x] 子任务 2.3.3: 实现时间线管理方法 ✅
  - `get_timeline()`: 获取完整时间线
  - `add_event(date, event)`: 添加事件
  - `update_current_date(date)`: 更新当前日期

- [x] 子任务 2.3.4: 实现角色状态管理方法 ✅
  - `update_character_status(name, **kwargs)`: 更新位置/状态/物品
  - `get_character_status(name)`: 获取角色状态
  - `add_item_to_character(name, item)`: 给角色添加物品
  - `remove_item_from_character(name, item)`: 从角色移除物品

- [x] 子任务 2.3.5: 实现伏笔管理方法 ✅
  - `add_foreshadowing(id, hint)`: 添加未回收伏笔
  - `resolve_foreshadowing(id)`: 标记伏笔已回收
  - `get_pending_foreshadowing()`: 获取未回收伏笔列表

---

## 任务 2.4: 实现检索与注入机制 (retriever.py)

创建 `MemoryRetriever` 类实现完整的检索流程。

- [x] 子任务 2.4.1: 创建 `MemoryRetriever` 类框架 ✅
  - 组合 `IndexLayer`, `DetailLayer`, `StateLayer`
  - 提供统一检索接口

- [x] 子任务 2.4.2: 实现查询意图解析 ✅
  - 通过关键词匹配判断查询类型
  - 类型：char（角色）、world（世界）、event（事件）、foreshadow（伏笔）

- [x] 子任务 2.4.3: 实现 `retrieve(query)` 方法 ✅
  - 搜索 L1 索引获取相关条目
  - 从 L2 详情层读取具体内容
  - 整合 L3 状态层的动态信息（如需要）
  - 返回不超过 500 字的上下文资料包

- [x] 子任务 2.4.4: 实现上下文打包 ✅
  - 拼接检索结果
  - 确保总长度不超过 500 字
  - 返回格式化的上下文字符串

---

## 任务 2.5: 实现 Auto Dream 记忆整合

在章节写作完成后自动整合记忆。

- [x] 子任务 2.5.1: 创建 `MemoryIntegrator` 类 ✅
  - 分析本章新增内容
  - 检测伏笔回收
  - 自动更新记忆文件

- [x] 子任务 2.5.2: 实现基于提示词的实体提取 ✅
  - 设计 LLM 提示词模板（提取角色、地点、伏笔）
  - 调用 LLM 从新章节草稿中提取结构化信息
  - 解析 LLM 返回的文本（格式：角色: 名称 | 描述）

- [x] 子任务 2.5.3: 实现去重逻辑 ✅
  - 添加前检查 memory_index.md 是否已存在同名条目
  - 使用 `IndexLayer.search()` 验证实体唯一性
  - 避免同一实体被反复添加

- [x] 子任务 2.5.4: 实现伏笔回收检测 ✅
  - 检查 pending_foreshadowing
  - 若伏笔关键词出现在新章节中，调用 `StateLayer.resolve_foreshadowing()`

- [x] 子任务 2.5.5: 实现记忆自动更新 ✅
  - 时间线自动推进（从草稿提取事件）
  - 角色状态自动更新（从草稿提取位置变化）
  - 索引和详情层同步更新

- [x] 子任务 2.5.6: 实现 `_extract_and_update_memory(draft_text)` 方法 ✅
  - 在 `agent.py` 的 `_handle_write_draft` 后调用
  - 整合上述所有子任务的功能

---

## 任务 2.6: 集成到工具层

将记忆系统与 `query_memory` 工具集成。

- [x] 子任务 2.6.1: 更新 `autowriter/src/tools/memory.py` 的 `query_memory` 工具 ✅
  - 使用 `MemoryRetriever` 实现真实检索
  - 返回格式化的上下文（不超过 500 字）

- [x] 子任务 2.6.2: 更新 `autowriter/src/core/agent.py` ✅
  - 在 `_handle_write_draft` 后调用 `_extract_and_update_memory()`
  - 确保每次章节写作后触发 Auto Dream 整合

- [x] 子任务 2.6.3: 可选：创建 `autowriter/src/memory/memory_manager.py` ✅
  - 将记忆相关操作封装成独立模块
  - 提供高层接口供 agent 调用

---

## 任务依赖关系

```
任务 2.1 (L1 索引层)
  └── 任务 2.2, 2.3 (L2/L3 详情状态层)

任务 2.2, 2.3 (L2/L3 详情状态层)
  └── 任务 2.4 (检索机制)

任务 2.4 (检索机制)
  └── 任务 2.5 (Auto Dream)

任务 2.5 (Auto Dream)
  └── 任务 2.6 (工具集成)
```

---

## 验收标准

1. **L1 索引层**：
   - 能够添加/删除/搜索索引条目
   - 格式符合 150 字符指针原则
   - 搜索返回相关度最高的 1-3 个条目

2. **L2 详情层**：
   - 能够根据锚点提取完整内容块
   - 支持在指定锚点下更新内容

3. **L3 状态层**：
   - 能够管理时间线、角色状态、伏笔
   - 结构化数据可序列化为 JSON

4. **检索机制**：
   - `retrieve(query)` 返回不超过 500 字的上下文
   - 检索结果包含相关角色/世界/事件的详细信息

5. **Auto Dream**：
   - 章节写作后自动检测新增实体
   - 伏笔回收检测准确
