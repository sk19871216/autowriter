# 阶段二：分层记忆系统规格文档

## Why

长篇小说的创作需要跨越数千字乃至数万字的上下文一致性。传统 AI 助手的上下文窗口限制会导致早期设定的遗忘、角色特征的前后矛盾、伏笔的遗忘回收。三层记忆模型通过索引-详情-状态的分离设计，实现：
1. **上下文精简**：每次 API 调用只注入 ~500 字索引，而非完整记忆
2. **按需加载**：仅当需要时才从详情层提取具体内容
3. **状态追踪**：结构化管理时间线、角色位置、伏笔状态等动态信息

## What Changes

### 1. 文件结构升级

```
my_novel/
└── .novel/
    ├── state.json                 # L3 状态层（扩展）
    ├── memory_index.md            # L1 索引层（关键）
    ├── memories/                  # L2 详情层
    │   ├── characters.md
    │   ├── worldview.md
    │   ├── timeline.md
    │   └── foreshadowing.md
    └── drafts/                    # 草稿
```

### 2. L1 索引层格式规范

**文件**：`memory_index.md`

**格式**：`类型 名称 | 简短描述 | 详情文件路径#锚点`

每行一个条目，使用 `|` 分隔三个字段：

```
char 林清瑶 | 女主，剑客，身负血仇，青云宗弟子 | memories/characters.md#林清瑶
char 柳慕白 | 男主，神秘游侠，身世成谜 | memories/characters.md#柳慕白
world 青云宗 | 云荒大陆东部剑道宗门 | memories/worldview.md#青云宗
world 破庙 | 废弃山神庙，常用场景 | memories/worldview.md#破庙
event 灭门惨案 | 十年前林家满门被灭，凶手未明 | memories/timeline.md#灭门惨案
foreshadow 剑鞘刻痕 | 林清瑶剑鞘上的刻痕，来历不明 | memories/foreshadowing.md#剑鞘刻痕
```

**设计要点**：
- 每行不超过 150 字符，保证索引完整放入每次 API 调用上下文
- 第三列是明确指针，告知系统去哪里找详细内容
- 允许手动编辑，但主要由系统自动维护

### 3. L2 详情层格式规范

**目录**：`memories/`

每个文件使用 Markdown 标题 + 段落结构，以 `# 标题` 作为检索锚点。

**characters.md 示例**：
```markdown
# 林清瑶
- 年龄：22岁
- 身份：青云宗弟子，林家遗孤
- 外貌：青衣，长剑，眉目清冷
- 性格：寡言，坚韧，外冷内热
- 武功：青云剑法第七重，剑势迅疾
- 关键经历：十岁时目睹灭门，被青云宗宗主柳青云救走

# 柳慕白
- 年龄：26岁
- 身份：游侠，自称来自西域
- 外貌：黑衣，斗笠，背负长刀
- 性格：洒脱不羁，言语戏谑，实则深藏心事
- 武功：刀法诡异，来历不明
```

**worldview.md 示例**：
```markdown
# 青云宗
- 位置：云荒大陆东部苍云山
- 势力：正道七宗之一，以剑道闻名
- 宗主：柳青云
- 特点：门规森严，弟子需下山历练三年

# 破庙
- 位置：苍云山北麓废弃山神庙
- 描述：年久失修，神像残破，常有旅人避雨
- 作用：多次作为故事场景
```

### 4. L3 状态层扩展

**文件**：`state.json`

扩展 `story_state` 结构：

```json
{
  "project_name": "my_novel",
  "current_chapter": 2,
  "drafts": { ... },
  "conversation_history": [ ... ],
  "story_state": {
    "timeline": {
      "current_date": "三月十五",
      "events": [
        {"date": "三月初一", "event": "林清瑶离开青云宗"},
        {"date": "三月初十", "event": "抵达苍云镇，遇柳慕白"}
      ]
    },
    "character_status": {
      "林清瑶": {
        "location": "破庙",
        "condition": "轻伤",
        "inventory": ["青云剑", "伤药"]
      }
    },
    "pending_foreshadowing": [
      {"id": "剑鞘刻痕", "status": "unresolved", "hint": "刻痕与灭门案有关"}
    ]
  }
}
```

### 5. 检索流程

当 Agent 调用 `query_memory(query)` 时，系统执行：

```
1. 解析查询意图（可选，初期可跳过）
   └─ 判断是角色、地点、事件还是伏笔（通过关键词匹配）

2. 搜索 L1 索引
   └─ 遍历 memory_index.md 每行，计算与 query 的相似度
   └─ 返回相似度最高的 1-3 个条目

3. 读取 L2 详情
   └─ 根据索引条目中的文件路径和锚点，读取对应文件
   └─ 定位到 # 标题 下的内容块

4. 整合 L3 结构化状态（如果需要）
   └─ 若查询涉及时间、位置等动态信息，从 state.json 提取

5. 返回结果
   └─ 将检索到的文本片段拼接
   └─ 形成不超过 500 字的上下文资料包
```

### 6. 检索算法选型

**初期方案**：简单规则 + 文本匹配，无需引入复杂向量数据库。

**相似度计算**：
- 关键词重叠率（Jaccard 相似度）
- 或基于关键词的 BM25

### 7. 详情内容提取

根据索引中的 `file_anchor`（如 `memories/characters.md#林清瑶`）：
1. 解析出文件路径和锚点标题
2. 从 Markdown 文件中提取该标题下的所有内容
3. 直到遇到下一个同级或更高级标题为止

## Impact

- **Affected specs**：
  - `novel-assistant-master/spec.md` - 分层记忆系统设计将作为独立子规格
  - 工具集工具描述需要更新以反映新的检索机制

- **Affected code**：
  - `autowriter/src/memory/` - 新增 `index_layer.py`, `detail_layer.py`, `state_layer.py`, `retriever.py`
  - `my_novel/.novel/` - 新增目录结构和文件

## ADDED Requirements

### Requirement: L1 索引层管理

系统 SHALL 提供 `IndexLayer` 类管理 `memory_index.md`：

**功能**：
- `add_entry(type, name, description, anchor)`: 添加索引条目
- `remove_entry(name)`: 删除索引条目
- `search(query, top_k=3)`: 搜索相似条目
- `update_entry(name, **kwargs)`: 更新索引条目

**格式验证**：
- 每行不超过 150 字符
- 使用 `|` 分隔三个字段
- 类型前缀为 `char`/`world`/`event`/`foreshadow`

### Requirement: L2 详情层管理

系统 SHALL 提供 `DetailLayer` 类管理 `memories/*.md`：

**功能**：
- `get_detail(file, anchor)`: 根据锚点获取详情内容
- `update_detail(file, anchor, content)`: 更新详情内容
- `create_anchor(file, anchor, content)`: 创建新的锚点条目

**文件组织**：
- `characters.md`: 角色档案
- `worldview.md`: 世界观/地点
- `timeline.md`: 时间线事件
- `foreshadowing.md`: 伏笔

### Requirement: L3 状态层管理

系统 SHALL 提供 `StateLayer` 类管理 `state.json`：

**功能**：
- `get_timeline()`: 获取时间线
- `add_event(date, event)`: 添加事件
- `update_character_status(name, **kwargs)`: 更新角色状态
- `get_character_status(name)`: 获取角色状态
- `add_foreshadowing(id, hint)`: 添加伏笔
- `resolve_foreshadowing(id)`: 标记伏笔已回收

### Requirement: 检索与注入机制

系统 SHALL 提供 `MemoryRetriever` 类实现检索流程：

**检索流程**：
1. 解析查询意图（char/world/event/foreshadow）
2. 在 L1 索引搜索相似条目（top_k=3）
3. 从 L2 详情层读取具体内容
4. 如需要，整合 L3 状态层的动态信息
5. 打包成不超过 500 字的上下文资料包

**注入时机**：
- 每次 API 调用前，注入完整 L1 索引
- 写作时按需检索 L2/L3

### Requirement: Auto Dream 记忆整合

系统 SHALL 在每次章节写作完成后自动整合记忆：

**流程**：
1. 分析本章新增的角色、地点、事件
2. 检测伏笔是否被回收
3. 更新时间线和角色状态
4. 自动维护索引和详情层

## MODIFIED Requirements

### Requirement: state.json 扩展

**原有**：`state.json` 只包含 `project_name`, `current_chapter`, `drafts`, `conversation_history`

**扩展后**：新增 `story_state` 字段，包含：
- `timeline`: 时间线和事件列表
- `character_status`: 角色位置、状态、物品
- `pending_foreshadowing`: 未回收伏笔列表

### Requirement: 轻量级记忆更新机制 (Auto Dream)

系统 SHALL 在每次章节草稿生成后自动更新记忆：

**触发时机**：
- 在 `_handle_write_draft` 生成正文后，调用 `_extract_and_update_memory(draft_text)`

**提取逻辑（基于提示词）**：
由于没有专门训练抽取模型，采用提示词抽取方式：用少量 Token 让 LLM 从新生成的文本中提取结构化信息。

**LLM 提示词模板**：
```
请从以下小说片段中提取：
1. 新出现的角色名（以及简要特征）
2. 新出现的地点/场景
3. 可能埋下的伏笔

输出格式：
角色: 名称 | 特征描述
地点: 名称 | 描述
伏笔: 内容描述
```

**去重逻辑**：
- 添加前先检查 memory_index.md 是否已存在同名条目
- 避免同一个实体被反复添加

**更新流程**：
1. 程序解析 LLM 返回的文本
2. 对每个新条目检查是否已存在
3. 将新条目追加到 `memory_index.md`
4. 将新详情追加到相应的 `memories/*.md` 文件

## 代码模块清单

| 文件 | 修改/新增内容 |
|------|--------------|
| `autowriter/src/memory/state_layer.py` | 增加读取/写入 memory_index.md 和详情文件的方法 |
| `autowriter/src/tools/memory.py` | 重写 `query_memory`，实现真实检索 |
| `autowriter/src/core/agent.py` | 在 `_handle_write_draft` 后调用记忆更新逻辑 |
| `autowriter/src/memory/memory_manager.py` | （可选）将记忆相关操作封装成独立模块 |

## 实现效果示例

**用户输入**：
```
📖 > 写一段林清瑶和柳慕白在破庙对话的场景。
```

**系统内部流程**：
1. Agent 调用 `query_memory("林清瑶")` → 返回详细角色档案
2. Agent 调用 `query_memory("柳慕白")` → 返回详细角色档案
3. Agent 调用 `query_memory("破庙")` → 返回场景描写参考
4. Agent 综合这些信息，调用 `write_draft` 生成符合人设的对话场景

**用户会看到**：
```
🔧 调用工具: query_memory
  参数: {"query": "林清瑶"}
👀 观察结果: 林清瑶，22岁，青云宗弟子...（详细档案）

🔧 调用工具: query_memory
  参数: {"query": "柳慕白"}
👀 观察结果: 柳慕白，26岁，神秘游侠...（详细档案）

✍️ 生成正文：
破庙里，林清瑶用剑拨了拨火堆，火星溅起。柳慕白倚着柱子，懒洋洋道："林姑娘的剑，比传闻中还快。"她没抬眼："你的刀也不慢。"
...
```

**效果**：
- 生成的对话符合已有设定（林清瑶寡言、柳慕白戏谑），因为 LLM 在写作时看到了角色档案
- 章节写作后，新出现的实体自动追加到记忆索引和详情文件

## Implementation Files

```
autowriter/src/memory/
├── __init__.py
├── index_layer.py      # L1 索引管理
├── detail_layer.py     # L2 详情管理
├── state_layer.py      # L3 状态管理
└── retriever.py        # 检索与注入

my_novel/.novel/
├── state.json          # 已存在，扩展结构
├── memory_index.md     # 已存在，标准化格式
└── memories/           # 已存在，标准化格式
    ├── characters.md
    ├── worldview.md
    ├── timeline.md
    └── foreshadowing.md
```
