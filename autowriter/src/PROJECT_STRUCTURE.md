# Autowriter 项目结构文档

## 目录结构

```
autowriter/src/
├── core/          # 核心引擎模块
├── llm/           # LLM 接口模块
├── memory/        # 记忆系统模块
└── tools/         # 工具集模块
```

---

## 1. core/ - 核心引擎模块

### agent.py
**WritingAgent** - 写作智能体（基于 ReAct 范式）

| 类/函数 | 功能 |
|---------|------|
| `WritingAgent` | ReAct 循环执行器，管理工具注册和调用 |
| `create_agent()` | 工厂函数，创建 WritingAgent 实例 |
| `_tool_write_draft()` | 工具：调用 LLM 生成章节草稿 |
| `_tool_revise_draft()` | 工具：根据指令修订已有章节 |
| `_extract_text_from_response()` | 从 API 响应中提取纯文本（过滤 ThinkingBlock） |
| `_update_memory_after_write()` | 写作后调用 Auto Dream 更新记忆 |
| `_save_chapter_to_file()` | 保存章节到 novel.md |
| `_load_style_rules()` | 加载写作风格规则 |

**核心流程**：
```
用户指令 → ReAct 循环 → 工具调用 → _tool_write_draft() → LLM API → 保存 novel.md
```

---

### engine.py
**WritingEngine** - 写作引擎 Hub（CLI 入口）

| 类/函数 | 功能 |
|---------|------|
| `WritingEngine` | 接收用户指令、意图解析、LangGraph 状态机管理 |
| `process_instruction()` | 解析用户指令并分发处理 |
| `_handle_write()` | 处理写章节指令 |
| `_handle_continue()` | 处理续写指令 |
| `_handle_revise()` | 处理修订指令 |
| `_handle_expand()` | 处理扩展大纲指令 |
| `_handle_query()` | 处理查询指令 |
| `_generate_draft()` | 生成章节草稿（⚠️ 当前为简单占位实现） |
| `_save_draft()` | 保存草稿到 drafts/ 目录 |
| `_load_draft()` | 从 drafts/ 目录加载草稿 |

**⚠️ 注意**：`_generate_draft()` 当前是简单实现，没有调用 `WritingAgent`。
**正确设计应该是**：`_generate_draft()` → `WritingAgent.execute_task()` → 返回内容 → `_save_draft()`

---

### react.py
**ReAct Loop** - 思考-行动-观察循环

| 类/函数 | 功能 |
|---------|------|
| `AgentState` | 枚举：THINKING, ACTION, OBSERVING, FINISH, ERROR |
| `ReActContext` | ReAct 执行上下文 |
| `ReActLoop` | ReAct 循环实现 |
| `_build_thinking_prompt()` | 构建思考阶段提示词 |
| `_execute_tools()` | 执行工具调用 |
| `ToolRegistry` | 工具注册表 |

**状态转换**：
```
THINKING → (LLM决定) → ACTION → OBSERVING → THINKING → ... → FINISH
```

---

### state.py
**状态模型** - 定义数据结构和状态类

| 类 | 功能 |
|-----|------|
| `WritingState` | 写作任务状态 |
| `ChapterState` | 章节状态 |
| `SessionState` | 会话状态 |
| `WritingContext` | 写作上下文（Engine 内部使用） |
| `WritingTask` | 写作任务定义 |
| `WritingResult` | 写作结果返回 |

---

## 2. llm/ - LLM 接口模块

### client.py
**LLMClient** - MiniMax Anthropic API 客户端

| 类/函数 | 功能 |
|---------|------|
| `LLMConfig` | LLM 配置类 |
| `LLMClient` | MiniMax API 封装（官方 Anthropic SDK） |
| `create_message()` | 发送消息并获取响应 |
| `call()` | 便捷方法（不使用工具，纯文本生成） |
| `call_with_tools()` | 调用 API（支持工具调用） |
| `parse_response()` | 解析响应，过滤 ThinkingBlock |
| `_extract_text_from_response()` | 从响应中提取纯文本 |
| `add_tool_result()` | 添加工具结果到缓冲区 |
| `flush_tool_results()` | 将工具结果作为单个 user 消息发送 |
| `add_llm_response()` | 保存 LLM 回复到消息历史 |
| `clear_history()` | 清空消息历史 |

**API 配置**：
- `base_url`: `https://api.minimaxi.com/anthropic`
- `model`: `MiniMax-M2.7`
- `api_key`: 环境变量 `ANTHROPIC_API_KEY` 或 `MINIMAX_START`

---

### message.py
**Message & Tool Definitions** - 消息和工具定义

| 类/函数 | 功能 |
|---------|------|
| `ToolDefinition` | 工具定义类 |
| `build_tool_definitions()` | 构建工具定义列表 |
| `build_system_prompt()` | 构建系统提示词 |

---

## 3. memory/ - 记忆系统模块

### index_layer.py
**L1 索引层** - 管理 memory_index.md

| 类 | 功能 |
|-----|------|
| `IndexEntry` | 索引条目类 |
| `IndexLayer` | 索引管理：读写 memory_index.md |

**索引格式**：`类型 名称 | 简短描述 | 详情文件路径#锚点`
- 类型：`char`, `world`, `event`, `foreshadow`
- 每行不超过 150 字符

---

### detail_layer.py
**L2 详情层** - 管理 memories/*.md

| 类 | 功能 |
|-----|------|
| `DetailLayer` | 详情管理：characters.md, worldview.md, timeline.md, foreshadowing.md |

**文件**：
- `characters.md` - 角色档案
- `worldview.md` - 世界观设定
- `timeline.md` - 事件时间线
- `foreshadowing.md` - 伏笔记录

---

### state_layer.py
**L3 状态层** - 管理 state.json

| 类 | 功能 |
|-----|------|
| `StateLayer` | 状态管理：读写 state.json |

**状态结构**：
```json
{
  "story_state": {
    "timeline": { "current_date": "", "events": [] },
    "character_status": {},
    "pending_foreshadowing": []
  }
}
```

---

### retriever.py
**MemoryRetriever** - 统一检索接口

| 类 | 功能 |
|-----|------|
| `MemoryRetriever` | 组合三层记忆，实现统一检索 |

**检索流程**：
```
用户查询 → 解析意图 → L1 索引搜索 → L2 详情获取 → L3 状态补充 → 返回上下文
```

**最大上下文长度**：500 字

---

### memory_integrator.py
**MemoryIntegrator** - Auto Dream 记忆整合

| 类 | 功能 |
|-----|------|
| `ExtractedEntity` | 提取的实体类 |
| `MemoryIntegrator` | Auto Dream：写作后自动提取和更新记忆 |

**功能**：
1. 使用 LLM 从章节草稿中提取结构化信息
2. 检测伏笔回收
3. 自动更新三层记忆

---

### __init__.py
**模块导出**

```python
from .index_layer import IndexLayer
from .detail_layer import DetailLayer
from .state_layer import StateLayer
from .retriever import MemoryRetriever
from .memory_integrator import MemoryIntegrator
```

---

## 4. tools/ - 工具集模块

### novel_tools.py
**NovelTools** - 写作辅助工具集

| 方法 | 功能 |
|------|------|
| `expand_outline()` | 将粗略想法扩展为场景级大纲 |
| `update_timeline()` | 记录事件或推进日期 |
| `check_foreshadowing()` | 查询所有未回收的伏笔 |
| `add_foreshadowing()` | 记录新的伏笔 |
| `resolve_foreshadowing()` | 标记伏笔已回收 |

---

### state_manager.py
**StoryStateManager** - 状态管理工具

| 方法 | 功能 |
|------|------|
| `get_timeline()` | 获取时间线 |
| `add_event()` | 添加事件到时间线 |
| `get_character_status()` | 查询角色状态 |
| `update_character_status()` | 更新角色状态 |
| `add_foreshadowing()` | 添加伏笔 |
| `resolve_foreshadowing()` | 标记伏笔已回收 |
| `get_pending_foreshadowing()` | 获取未回收伏笔 |

---

### memory.py
**QueryMemoryTool** - 查询记忆工具

| 类/方法 | 功能 |
|---------|------|
| `QueryMemoryTool` | 查询记忆工具类 |
| `execute()` | 执行查询，返回上下文文本 |
| `get_full_index()` | 获取完整 L1 索引 |
| `get_schema()` | 获取工具 schema |

---

## 架构流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                            │
│                  (自然语言指令输入)                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WritingEngine (Hub)                            │
│  - process_instruction: 接收和解析用户指令                        │
│  - 意图识别 (Intent Parsing)                                     │
│  - _handle_write / _handle_continue / _handle_revise            │
│  - _save_draft / _load_draft (drafts/ 目录)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WritingAgent (Brain)                          │
│  - ReAct 循环执行 (react.py)                                     │
│  - 工具注册与调用                                                │
│  - _tool_write_draft / _tool_revise_draft                       │
│  - _update_memory_after_write (Auto Dream)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   LLMClient     │ │   ToolRegistry  │ │  MemoryRetriever│
│  (llm/client.py)│ │  (tools/)      │ │  (memory/)      │
└─────────────────┘ └─────────────────┘ └─────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
            ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
            │ L1 IndexLayer │     │ L2 DetailLayer│     │ L3 StateLayer │
            │memory_index.md│     │ memories/*.md │     │   state.json  │
            └───────────────┘     └───────────────┘     └───────────────┘
```

---

## 工具清单 (11个)

| 工具名称 | 所在文件 | 功能 |
|---------|---------|------|
| `query_memory` | tools/memory.py | 查询角色/世界观信息 |
| `write_draft` | core/agent.py | 创作新章节 |
| `revise_draft` | core/agent.py | 修订已有章节 |
| `expand_outline` | tools/novel_tools.py | 扩展大纲 |
| `update_timeline` | tools/novel_tools.py | 更新时间线 |
| `check_foreshadowing` | tools/novel_tools.py | 查询未回收伏笔 |
| `add_foreshadowing` | tools/novel_tools.py | 添加新伏笔 |
| `resolve_foreshadowing` | tools/novel_tools.py | 标记伏笔已回收 |
| `get_character_status` | tools/state_manager.py | 查询角色状态 |
| `update_character_status` | tools/state_manager.py | 更新角色状态 |
| `finish_task` | core/agent.py | 报告任务完成 |

---

## 数据文件结构

```
my_novel/
├── novel.md                 # 最终成品（所有章节合并）
├── outline.md               # 大纲
└── .novel/                  # 系统内部状态
    ├── memory_index.md      # L1 索引
    ├── state.json           # L3 状态
    ├── memories/
    │   ├── characters.md    # 角色详情
    │   ├── worldview.md     # 世界观详情
    │   ├── timeline.md      # 事件详情
    │   └── foreshadowing.md # 伏笔详情
    └── drafts/             # 章节草稿目录
        ├── chapter_001.md   # 第1章草稿
        ├── chapter_002.md   # 第2章草稿
        └── ...
```

---

## ⚠️ 已知问题（已修复）

~~1. **`WritingEngine._generate_draft()` 是简单占位实现**，没有调用 `WritingAgent`~~
~~2. **`WritingAgent._save_chapter_to_file()` 直接写入 `novel.md`**，跳过了 `drafts/` 目录~~

### ✅ 已修复

1. **`WritingEngine._generate_draft()`** 现在调用 `WritingAgent.execute_task()`
2. **`WritingAgent._tool_write_draft()`** 不再直接保存到 `novel.md`，只返回内容
3. **新增 `finish_task` 工具**，用于报告任务完成
4. **`write_draft` prompt** 包含未回收伏笔信息，引导 LLM 在写作时考虑伏笔

### 正确流程

```
用户指令 → WritingEngine._handle_write()
         → WritingEngine._generate_draft()
         → WritingAgent.execute_task()
         → ReAct 循环 + 工具调用
         → _tool_write_draft() 返回内容
         → WritingEngine._save_draft() 保存到 drafts/chapter_XXX.md
         → 用户确认后手动写入 novel.md
```
