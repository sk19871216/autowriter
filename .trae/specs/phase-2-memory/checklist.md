# 检查清单 - 阶段二：分层记忆系统

本文档用于验证阶段二实现是否满足规格要求。

---

## L1 索引层检查 (index_layer.py)

- [x] `IndexLayer` 类已创建在 `autowriter/src/memory/index_layer.py` ✅
- [x] 构造函数接收 `novel_path` 参数 ✅
- [x] `add_entry(type, name, description, anchor)` 方法实现 ✅
- [x] `remove_entry(name)` 方法实现 ✅
- [x] `search(query, top_k=3)` 方法实现，返回相似度最高的条目 ✅
- [x] `update_entry(name, **kwargs)` 方法实现 ✅
- [x] 格式验证：每行不超过 150 字符 ✅
- [x] 格式验证：使用 `|` 分隔三个字段 ✅
- [x] 格式验证：类型前缀为 `char`/`world`/`event`/`foreshadow` ✅

---

## L2 详情层检查 (detail_layer.py)

- [x] `DetailLayer` 类已创建在 `autowriter/src/memory/detail_layer.py` ✅
- [x] `get_detail(file, anchor)` 方法实现，能提取锚点下的内容块 ✅
- [x] `update_detail(file, anchor, content)` 方法实现 ✅
- [x] `create_anchor(file, anchor, content)` 方法实现 ✅
- [x] `characters.md` 文件格式标准化 ✅
- [x] `worldview.md` 文件格式标准化 ✅
- [x] `timeline.md` 文件格式标准化 ✅
- [x] `foreshadowing.md` 文件格式标准化 ✅

---

## L3 状态层检查 (state_layer.py)

- [x] `StateLayer` 类已创建在 `autowriter/src/memory/state_layer.py` ✅
- [x] `story_state` 结构已扩展（timeline, character_status, pending_foreshadowing）✅
- [x] `get_timeline()` 方法实现 ✅
- [x] `add_event(date, event)` 方法实现 ✅
- [x] `update_character_status(name, **kwargs)` 方法实现 ✅
- [x] `get_character_status(name)` 方法实现 ✅
- [x] `add_foreshadowing(id, hint)` 方法实现 ✅
- [x] `resolve_foreshadowing(id)` 方法实现 ✅
- [x] `get_pending_foreshadowing()` 方法实现 ✅
- [x] JSON 序列化/反序列化正确 ✅

---

## 检索与注入机制检查 (retriever.py)

- [x] `MemoryRetriever` 类已创建在 `autowriter/src/memory/retriever.py` ✅
- [x] 查询意图解析实现（char/world/event/foreshadow）✅
- [x] `retrieve(query)` 方法实现完整检索流程 ✅
- [x] 上下文打包不超过 500 字 ✅
- [x] 检索结果包含相关角色/世界/事件的详细信息 ✅

---

## Auto Dream 记忆整合检查

- [x] `_extract_and_update_memory(draft_text)` 方法在 `write_draft` 后调用 ✅
- [x] LLM 提示词抽取实现（提取角色、地点、伏笔）✅
- [x] 去重逻辑实现，避免同一实体被反复添加 ✅
- [x] 新增实体自动追加到 `memory_index.md` ✅
- [x] 新增详情自动追加到相应 `memories/*.md` 文件 ✅
- [x] 伏笔回收检测实现 ✅

---

## 工具集成检查

- [x] `query_memory` 工具使用 `MemoryRetriever` 实现 ✅
- [x] `write_draft` 工具在写作前注入 L1 索引 ✅
- [x] `write_draft` 工具在写作后触发 Auto Dream 整合 ✅

---

## 文件路径检查

- [x] `autowriter/src/memory/__init__.py` 导出所有记忆模块 ✅
- [x] `autowriter/src/memory/index_layer.py` 存在 ✅
- [x] `autowriter/src/memory/detail_layer.py` 存在 ✅
- [x] `autowriter/src/memory/state_layer.py` 存在 ✅
- [x] `autowriter/src/memory/retriever.py` 存在 ✅
- [x] `my_novel/.novel/memory_index.md` 存在且格式正确 ✅
- [x] `my_novel/.novel/memories/characters.md` 存在 ✅
- [x] `my_novel/.novel/memories/worldview.md` 存在 ✅
- [x] `my_novel/.novel/memories/timeline.md` 存在 ✅
- [x] `my_novel/.novel/memories/foreshadowing.md` 存在 ✅
- [x] `my_novel/.novel/state.json` 已扩展 story_state 结构 ✅

---

## 功能验证检查

### 场景：林清瑶和柳慕白在破庙对话

- [ ] 调用 `query_memory("林清瑶")` 返回详细角色档案（待运行时验证）
- [ ] 调用 `query_memory("柳慕白")` 返回详细角色档案（待运行时验证）
- [ ] 调用 `query_memory("破庙")` 返回场景描写参考（待运行时验证）
- [ ] 生成对话符合已有设定（林清瑶寡言、柳慕白戏谑）（待运行时验证）
- [ ] 章节写作后记忆自动更新到索引和详情层（待运行时验证）

---

## 阶段二验收状态

- [x] 阶段二核心功能实现完成 ✅
- [x] 检索机制返回结果不超过 500 字 ✅
- [x] 格式验证全部通过 ✅
- [x] 工具集成完成 ✅
- [x] Auto Dream 记忆整合完成 ✅
