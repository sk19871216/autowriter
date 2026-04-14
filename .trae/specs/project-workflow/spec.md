# 项目工作流程规格文档

## Why

全面梳理 Autowriter 小说写作智能体系统的架构与工作流程，确保开发团队对系统有统一的认知，并作为后续功能扩展和代码维护的参考文档。

## What Changes

### 1. 系统架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                           │
│                    (自然语言指令输入)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WritingEngine (Hub)                          │
│  - process_instruction: 接收和解析用户指令                        │
│  - 意图识别 (Intent Parsing)                                     │
│  - LangGraph StateGraph 构建                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WritingAgent (Brain)                         │
│  - 基于 ReAct 范式的思考-行动-观察循环                            │
│  - 工具注册与调用                                                │
│  - 写作任务执行                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   LLM Client    │ │  Tool Registry  │ │  Memory System  │
│ (MiniMax API)   │ │ (9 写作工具)     │ │  (三层记忆)      │
└─────────────────┘ └─────────────────┘ └─────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
            ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
            │ L1 Index Layer │     │ L2 Detail Layer│     │ L3 State Layer │
            │ memory_index  │     │ memories/*.md │     │   state.json   │
            └───────────────┘     └───────────────┘     └───────────────┘
```

### 2. 核心模块职责

| 模块 | 文件路径 | 核心职责 |
|------|---------|---------|
| **Engine** | `autowriter/src/core/engine.py` | 接收用户指令、意图解析、LangGraph 状态机管理 |
| **Agent** | `autowriter/src/core/agent.py` | ReAct 循环执行、工具调用、写作任务调度 |
| **ReAct Loop** | `autowriter/src/core/react.py` | Think-Action-Observation 循环逻辑 |
| **LLM Client** | `autowriter/src/llm/client.py` | MiniMax Anthropic API 封装 |
| **Memory Retriever** | `autowriter/src/memory/retriever.py` | 统一检索接口（组合三层记忆） |
| **Memory Integrator** | `autowriter/src/memory/memory_integrator.py` | Auto Dream - 写作后自动提取更新记忆 |
| **Index Layer** | `autowriter/src/memory/index_layer.py` | L1 索引管理（memory_index.md） |
| **Detail Layer** | `autowriter/src/memory/detail_layer.py` | L2 详情管理（memories/*.md） |
| **State Layer** | `autowriter/src/memory/state_layer.py` | L3 状态管理（state.json） |
| **Novel Tools** | `autowriter/src/tools/novel_tools.py` | 写作辅助工具集 |
| **Story State Manager** | `autowriter/src/tools/state_manager.py` | 故事状态管理器 |

### 3. 工具清单与分类

#### 3.1 记忆工具

| 工具名称 | 功能 | 触发时机 |
|---------|------|---------|
| `query_memory` | 查询角色、世界观或故事背景信息 | 需要了解设定时 |

#### 3.2 写作工具

| 工具名称 | 功能 | 触发时机 |
|---------|------|---------|
| `write_draft` | 根据大纲创作新的章节文本 | 具备足够背景信息后开始写作 |
| `revise_draft` | 根据修改指令修订已有章节 | 需要调整已有内容时 |
| `expand_outline` | 将粗略想法扩展为场景级大纲 | 用户只给出一句话梗概时 |

#### 3.3 时间线工具

| 工具名称 | 功能 | 触发时机 |
|---------|------|---------|
| `update_timeline` | 记录事件或推进日期 | 章节涉及时间推移或关键事件时 |

#### 3.4 伏笔管理工具

| 工具名称 | 功能 | 触发时机 |
|---------|------|---------|
| `check_foreshadowing` | 查询所有未回收的伏笔 | 写作前构思情节时 |
| `add_foreshadowing` | 记录新的伏笔 | 章节中埋下伏笔时 |
| `resolve_foreshadowing` | 标记伏笔已回收 | 伏笔被揭晓时 |

#### 3.5 角色状态工具

| 工具名称 | 功能 | 触发时机 |
|---------|------|---------|
| `get_character_status` | 查询角色当前位置、状态、物品 | 描写角色出场前 |
| `update_character_status` | 更新角色的位置、状态、物品 | 角色状态发生变化时 |

### 4. 三层记忆系统

#### L1 - 索引层 (Index Layer)
- **文件**: `my_novel/.novel/memory_index.md`
- **格式**: `类型 名称 | 简短描述 | 详情文件路径#锚点`
- **功能**: 快速检索入口，指向详细记忆

#### L2 - 详情层 (Detail Layer)
- **文件**: `my_novel/.novel/memories/*.md`
  - `characters.md` - 角色档案
  - `worldview.md` - 世界观设定
  - `timeline.md` - 事件时间线
  - `foreshadowing.md` - 伏笔记录
- **功能**: 存储实体的详细信息

#### L3 - 状态层 (State Layer)
- **文件**: `my_novel/.novel/state.json`
- **结构**:
  ```json
  {
    "story_state": {
      "timeline": { "current_date": "...", "events": [...] },
      "character_status": { "角色名": { "location": "", "condition": "", "inventory": [] } },
      "pending_foreshadowing": [...]
    }
  }
  ```
- **功能**: 管理动态状态（角色位置、时间线进度、未回收伏笔）

### 5. ReAct 循环流程

```
                    ┌─────────────────┐
                    │   User Message   │
                    └────────┬────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                     ReAct Loop (max 50 iter)                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐                                           │
│  │   THINKING    │◄─────────────────────────────────┐       │
│  └───────┬───────┘                                  │       │
│          │ LLM decides:                             │       │
│          │ - use tool → ACTION                      │       │
│          │ - finish / "FINISH" → FINISH            │       │
│          │ - no tools → continue THINKING          │       │
│          │                                           │       │
│          ▼                                           │       │
│  ┌──────────────┐                                   │       │
│  │    ACTION     │──────────► Tool Execution        │       │
│  └───────┬───────┘                                   │       │
│          │                                           │       │
│          │ Tool Result                                │       │
│          ▼                                           │       │
│  ┌──────────────┐                                   │       │
│  │   OBSERVING  │──────────► Add to history         │       │
│  └──────────────┘                                   │       │
│          │                                           │       │
│          └───────────────────────────────────────────┘       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     FINISH      │
                    │ (return result) │
                    └─────────────────┘
```

### 6. 典型写作流程

```
用户输入: "请写第3章，林清瑶在苍云镇集市发现灭门案线索"
          │
          ▼
┌─────────────────────────────────────────────────────┐
│ 1. Intent Parsing                                    │
│    → type: "write", chapter: 3                      │
└─────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────┐
│ 2. ReAct Loop - Think                                │
│    LLM: "用户要写第3章，我需要先查询相关背景信息..."    │
│    Decision: use query_memory tool                   │
└─────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────┐
│ 3. ReAct Loop - Action                               │
│    Execute: query_memory("苍云镇 灭门案")             │
│    Return: 苍云镇设定、灭门案背景...                  │
└─────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────┐
│ 4. ReAct Loop - Think                                │
│    LLM: "现在我有背景信息了，可以开始写作..."         │
│    Decision: use write_draft tool                   │
└─────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────┐
│ 5. ReAct Loop - Action                               │
│    Execute: write_draft(chapter=3, outline=...)      │
│    Return: 章节草稿内容                               │
└─────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────┐
│ 6. Auto Dream (Memory Integration)                   │
│    - extract_and_update_memory(draft)               │
│    - 检测新角色、新地点、新伏笔                       │
│    - 更新 L1/L2/L3 记忆层                           │
└─────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────┐
│ 7. Save Draft                                        │
│    → my_novel/novel.md (追加第3章)                  │
└─────────────────────────────────────────────────────┘
          │
          ▼
                    FINISH - 返回结果给用户
```

### 7. 指令类型与处理

| 指令类型 | 关键词 | 处理逻辑 |
|---------|--------|---------|
| **write** | "写" + "章" | 解析章节号，加载大纲，执行写作任务 |
| **continue** | "继续"、"续写" | 加载上一章草稿，生成续写内容 |
| **revise** | "修改"、"改"、"调整" | 加载指定章节，应用修改指令 |
| **expand** | "大纲"、"扩展"、"细化" | 调用 expand_outline 工具 |
| **query** | "查询"、"问"、"什么" | 调用 query_memory 工具 |

### 8. 配置管理

| 配置类 | 用途 |
|--------|------|
| `LLMConfig` | MiniMax API 配置（api_key, base_url, model） |
| `ProjectConfig` | 项目路径配置（novel_dir, system_dir） |
| `MemoryConfig` | 记忆系统配置（索引长度限制） |
| `WritingConfig` | 写作引擎配置（压缩阈值、续写标记） |
| `ValidationConfig` | 验证流水线配置 |
| `ReActConfig` | ReAct 循环配置（最大迭代次数） |

### 9. 文件结构

```
autowriter/
├── config/
│   └── settings.py          # 系统配置
├── src/
│   ├── core/
│   │   ├── agent.py         # WritingAgent (ReAct Brain)
│   │   ├── engine.py        # WritingEngine (Hub)
│   │   ├── react.py        # ReAct Loop
│   │   └── state.py        # State Models
│   ├── llm/
│   │   ├── client.py        # MiniMax API Client
│   │   └── message.py      # Message/Tool Definitions
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── index_layer.py  # L1 Index
│   │   ├── detail_layer.py # L2 Detail
│   │   ├── state_layer.py  # L3 State
│   │   ├── retriever.py    # Unified Retrieval
│   │   └── memory_integrator.py # Auto Dream
│   └── tools/
│       ├── __init__.py
│       ├── novel_tools.py   # Writing Tools
│       ├── state_manager.py # Story State Manager
│       └── memory.py        # Memory Tools
└── tests/                   # 测试文件

my_novel/
├── novel.md                 # 小说正文
├── outline.md               # 大纲
└── .novel/                  # 系统目录
    ├── memory_index.md      # L1 索引
    ├── state.json           # L3 状态
    ├── memories/
    │   ├── characters.md    # 角色详情
    │   ├── worldview.md     # 世界观详情
    │   ├── timeline.md      # 事件详情
    │   └── foreshadowing.md # 伏笔详情
    └── drafts/             # 草稿目录
```

## Impact

- **本规格文档**: `project-workflow/spec.md`
- **相关规格**:
  - `phase-2-memory/spec.md` - 记忆系统详细规格
  - `phase-3-tools/spec.md` - 工具化扩展规格
  - `novel-assistant-master/spec.md` - 主规格文档

## ADDED Requirements

### Requirement: 项目架构文档

系统 SHALL 提供完整的工作流程文档，描述各模块的职责、交互关系和数据流。

### Requirement: 工具链说明

系统 SHALL 提供工具调用链的说明，包括典型场景下的工具调用顺序。

### Requirement: 状态转换图

系统 SHALL 提供 ReAct 循环的状态转换图，明确各状态的转换条件。
