# 小说助手系统规格文档

## Why

长篇小说的创作面临上下文容量限制、记忆一致性维护、多工具协作等核心挑战。本系统借鉴 Claude Code 的工程化思路，通过模块化的 WritingAgent 枢纽、分层记忆体系、工具化能力封装，构建一个可持续、可中断、可验证的 AI 辅助写作框架。

## What Changes

本项目将实现一个基于 **MiniMax M2.7** 模型和 **ReAct 范式** 的小说创作助手，包含以下核心模块：

1. **WritingAgent 核心枢纽** - 基于 ReAct (Reasoning and Acting) 范式，负责思考-行动-观察的循环决策
2. **LLMClient 模块** - 封装 MiniMax API 调用，管理会话历史和消息格式
3. **分层记忆系统** - 三层记忆模型（L1 索引层、L2 详情层、L3 状态层）
4. **工具化能力模块** - 三个核心工具（query_memory, write_draft, revise_draft）
5. **三明治 Prompt 架构** - 上层基石、中层资料、下层强调的分层 Prompt 设计
6. **一致性验证流水线** - Postwriter 风格的多维度自动检查

## Impact

- Affected capabilities: 长篇叙事一致性维护、多角色多线叙事追踪、伏笔管理回收、迭代式写作改进
- Affected code: 核心架构基于 ReAct 循环，持久化基于文件系统，API 调用基于 MiniMax M2.7
- API Provider: **MiniMax** (使用 TRAE 配置的 API)

## LLM API 配置

### Provider: MiniMax

| 参数 | 默认值 | 说明 |
|------|--------|------|
| model | MiniMax M2.7 | 默认使用 MiniMax 最新模型 |
| api_key | 从环境变量加载 | MINIMAX_API_KEY |
| base_url | MiniMax API 端点 | https://api.minimax.chat |
| temperature | 0.7 | 写作时可适当提高 |
| max_tokens | 4000 | 单次响应最大 Token 数 |

### 环境变量

```bash
MINIMAX_API_KEY=your_api_key
MINIMAX_BASE_URL=https://api.minimax.chat/v1
```

## ADDED Requirements

### Requirement: WritingAgent 核心枢纽 (ReAct 范式)

WritingAgent 是系统的"大脑"，基于 ReAct 范式实现思考-行动-观察的循环：

```
┌─────────────────────────────────────────────────────┐
│                    ReAct 循环                       │
├─────────────────────────────────────────────────────┤
│  Thought: 根据当前任务，决定下一步该做什么           │
│      ↓                                              │
│  Action: 选择并调用一个 Tool                         │
│      ↓                                              │
│  Observation: 获取 Tool 返回的结果                   │
│      ↓                                              │
│  Loop: 将观察结果作为新上下文，进入下一轮思考         │
│      ↓                                              │
│  Finish: 任务完成，输出结果                          │
└─────────────────────────────────────────────────────┘
```

**状态定义**：
- `THINKING`: 思考下一步行动
- `ACTION`: 执行工具调用
- `OBSERVING`: 观察工具返回结果
- `FINISH`: 任务完成
- `ERROR`: 发生错误，需要处理

#### Scenario: 章节写作思维链
- **WHEN** 用户输入"写第三章：林清瑶夜探藏剑阁"
- **THEN** Agent 进入 ReAct 循环：
  1. **Thought**: "我需要先了解藏剑阁的布局和林清瑶的能力"
  2. **Action**: 调用 `query_memory("藏剑阁")` 和 `query_memory("林清瑶")`
  3. **Observation**: 收到地点描写和角色档案
  4. **Thought**: "现在我有足够信息，可以开始写作了"
  5. **Action**: 调用 `write_draft(chapter=3, outline="...")`
  6. **Observation**: 收到生成的草稿
  7. **Finish**: 输出草稿到磁盘

### Requirement: LLMClient 模块

LLMClient 负责与 MiniMax API 交互，是 WritingAgent 的"大脑皮层"：

**职责**：
- 将 Agent 的思考结果、工具调用请求组装成 MiniMax API 所需的消息格式
- 发送 HTTP 请求并处理响应
- 解析 API 返回的工具调用指令
- 管理会话历史，确保每次调用携带完整上下文

**消息格式**：
```json
{
  "model": "MiniMax M2.7",
  "messages": [
    {"role": "system", "content": "[System Prompt]"},
    {"role": "user", "content": "[User Input]"},
    {"role": "assistant", "content": "[History]"}
  ],
  "tools": [...],
  "temperature": 0.7,
  "max_tokens": 4000
}
```

### Requirement: System Prompt 模板

WritingAgent 的身份和行为模式通过 System Prompt 定义：

```
你是专业的小说写作智能体（WritingAgent）。
你的目标是协助用户完成小说章节的创作。

【可用工具】
- query_memory: 当你需要查询角色、世界观或任何故事背景信息时使用。
  输入: {"query": "角色名或地点名"}
  输出: 相关角色/世界观档案文本

- write_draft: 根据给定的大纲和上下文，创作新的文本。
  输入: {"chapter": 章节号, "outline": "章节大纲", "context": "上下文"}
  输出: 生成的章节草稿

- revise_draft: 根据指令，修改已有的文本。
  输入: {"chapter": 章节号, "instruction": "修改指令", "current_draft": "当前草稿"}
  输出: 修改后的草稿

【行为规则】
1. 始终遵循 ReAct 框架进行推理和行动
2. 每次行动前先思考（Thought）
3. 确保生成内容符合小说风格设定
4. 保持角色性格一致性
5. 及时埋设和回收伏笔

【写作风格】
- [从 outline.md 或配置中加载]
```

### Requirement: 分层记忆系统

系统 SHALL 实现三层记忆模型：

| 层级 | 存储形式 | 加载时机 | 容量目标 |
|------|----------|----------|----------|
| L1 索引层 | memory_index.md | 每次 API 调用完整注入 | ~500 字 |
| L2 详情层 | memories/*.md | 按需检索注入 | 按需 |
| L3 状态层 | state.json | 结构化注入，每次写作前更新 | 结构化数据 |

**索引格式（150字符指针原则）**：
```
char 林清瑶 | 女主，剑客，身负血仇 | 详见 memories/characters.md#林清瑶
world 藏剑阁 | 青云宗禁地 | 详见 memories/worldview.md#藏剑阁
plot 灭门案 | 第1章发生，凶手未明 | 详见 memories/foreshadowing.md#灭门案
```

### Requirement: 核心工具集

| 工具名 | 功能 | 触发时机 |
|--------|------|----------|
| query_memory | 查询角色/世界观等知识库 | 需要查询故事背景时 |
| write_draft | 根据大纲生成初稿 | 产出正文时 |
| revise_draft | 根据反馈修改文本 | 需要修订时 |

#### Scenario: 工具自主调用
- **WHEN** 模型收到"写林清瑶夜探藏剑阁"
- **THEN** 模型自主决定调用 `query_memory("藏剑阁")` 和 `query_memory("林清瑶")`，然后调用 `write_draft`

### Requirement: 三明治 Prompt 架构

write_draft 的 Prompt 严格分为三层：

- **上层（注意力最强）**：写作风格定义、本章铁律
- **中层（注意力较弱）**：角色档案、地点描写、前情提要、本章大纲
- **下层（注意力第二强）**：Remember: 前缀强调关键指令

### Requirement: 续写标记机制

每次 write_draft 结束时输出 [续写标记]，包含：
- 当前场景最后一句话
- 未写完的动作
- 接下来要发生的下一件事

下次续写时将此标记注入 Prompt 开头。

### Requirement: 动态压缩策略

- **WHEN** 已生成本章正文超过 3000 字
- **THEN** 触发压缩：用 200 字摘要替代早期部分，保留最近 500 字原文

### Requirement: 一致性验证流水线

每章草稿完成后自动触发验证流程，检查：
- 事实一致性（人物特征、时间线）
- 伏笔状态（是否回收、是否引入新伏笔）
- 角色行为逻辑
- 对话风格一致性

验证器输出结构化检查报告：
```json
{
  "inconsistencies": [...],
  "unresolved_foreshadowing": [...],
  "suggestions": [...]
}
```

### Requirement: 设定传播与惰性更新

- **WHEN** 用户修改基础设定
- **THEN** 系统标记受影响章节为"待修订"
- **WHEN** 用户打开待修订章节
- **THEN** 系统提示用户确认是否修订

## Project Structure

```
autowriter/                         # 项目代码根目录
├── src/
│   ├── __init__.py
│   ├── core/                       # 核心枢纽
│   │   ├── __init__.py
│   │   ├── agent.py               # WritingAgent (ReAct 循环)
│   │   ├── state.py               # 状态管理 (THINKING/ACTION/OBSERVING/FINISH)
│   │   └── react.py               # ReAct 循环逻辑
│   ├── llm/                       # LLM 接口层 ⭐ 新增
│   │   ├── __init__.py
│   │   ├── client.py             # LLMClient (MiniMax API 封装)
│   │   └── message.py            # 消息格式处理
│   ├── memory/                    # 记忆系统
│   │   ├── __init__.py
│   │   ├── index_layer.py        # L1 索引管理
│   │   ├── detail_layer.py       # L2 详情管理
│   │   └── state_layer.py        # L3 状态管理
│   ├── tools/                    # 工具集
│   │   ├── __init__.py
│   │   ├── base.py               # 工具基类
│   │   ├── memory.py             # query_memory
│   │   ├── writer.py             # write_draft
│   │   └── reviser.py            # revise_draft
│   ├── prompt/                   # Prompt 管理
│   │   ├── __init__.py
│   │   ├── system.py            # System Prompt 模板
│   │   ├── sandwich.py           # 三明治结构
│   │   └── templates.py          # 工具描述模板
│   ├── validator/                # 验证流水线
│   │   ├── __init__.py
│   │   ├── checker.py            # 检查器基类
│   │   └── report.py             # 报告生成
│   ├── interface/                # 交互界面
│   │   ├── __init__.py
│   │   ├── parser.py             # 指令解析
│   │   └── dashboard.py          # 看板展示
│   └── utils/                    # 工具函数
│       ├── __init__.py
│       ├── file_ops.py           # 文件操作
│       └── compression.py        # 压缩工具
├── config/
│   └── settings.py               # 配置管理 (含 MiniMax 配置)
├── tests/
├── pyproject.toml
└── README.md

my_novel/                           # 小说工程根目录
├── .novel/                         # 系统内部状态
│   ├── memory_index.md            # L1 索引层
│   ├── memories/                  # L2 详情层
│   ├── drafts/                    # 章节草稿
│   └── state.json                 # L3 状态层
├── outline.md                     # 用户大纲
└── novel.md                       # 最终成品
```

## ReAct 循环伪代码

```python
def run_react_loop(agent, task):
    """ReAct 核心循环"""
    state = "THINKING"
    observation = None
    history = []

    while state != "FINISH" and state != "ERROR":
        if state == "THINKING":
            # 构建思考 Prompt
            prompt = build_thought_prompt(task, history, observation)
            response = agent.llm.call(prompt)

            # 解析响应中的 Action
            if response.has_action():
                action = response.extract_action()
                state = "ACTION"
            elif response.is_finish():
                state = "FINISH"
                result = response.content
            else:
                observation = response.content
                state = "THINKING"

        elif state == "ACTION":
            # 执行工具
            tool_result = agent.execute_tool(action)
            history.append({
                "action": action,
                "result": tool_result
            })
            observation = tool_result
            state = "THINKING"

    return result
```

## Implementation Phases

### Phase 1: 系统骨架

1. 创建项目目录结构 ✅
2. 实现 LLMClient 模块（MiniMax API 封装）
3. 实现 WritingAgent 核心（ReAct 循环）
4. 实现最简工具集（query_memory, write_draft, revise_draft）

### Phase 2: 分层记忆

1. 实现 L1 索引的读写和检索
2. 实现 L2 详情层文件管理
3. 实现 L3 状态层结构化管理
4. 实现检索与注入机制

### Phase 3: 工具化完善

1. 实现完整的工具描述模板
2. 实现工具注册和动态调用
3. 实现 Auto Dream 记忆整合

### Phase 4: 写作引擎优化

1. 实现三明治 Prompt 架构
2. 实现续写标记机制
3. 实现动态压缩策略

### Phase 5: 一致性检查

1. 实现验证智能体
2. 实现结构化报告生成
3. 实现设定传播与惰性更新

### Phase 6: 交互界面

1. 实现自然语言指令解析
2. 实现创作看板可视化
3. 实现 CLI 界面
