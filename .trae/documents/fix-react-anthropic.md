# 修复计划：使用 Anthropic API 格式修复 ReAct 循环

## 问题分析

当前 ReAct 循环使用 `tools` 参数的 OpenAI 格式与 MiniMax API 不兼容：
- 错误: `tool result's tool id(call_1) not found`
- 原因: MiniMax 需要 Anthropic 兼容格式

## MiniMax 官方文档关键信息

1. **API 端点**: `https://api.minimaxi.com/anthropic`
2. **认证**: `ANTHROPIC_API_KEY` 环境变量
3. **消息格式**:
   - `type: "text"` - 文本消息
   - `type: "tool_use"` - 工具调用
   - `type: "tool_result"` - 工具调用结果
4. **关键**: 多轮对话时必须完整回传 `response.content`

---

## 实施步骤

### 步骤 1: 更新配置 `config/settings.py`

```python
class LLMConfig(BaseModel):
    base_url: str = "https://api.minimaxi.com/anthropic"  # 改为 Anthropic 端点
```

### 步骤 2: 重写 LLMClient `src/llm/client.py`

使用 Anthropic 兼容格式：

1. **修改 `call_with_tools` 方法**:
   - 不再使用 `tools` 参数
   - 改为在消息中添加工具说明
   - 解析 `tool_use` 块

2. **修改 `add_tool_result` 方法**:
   - 使用 `type: "tool_result"` 格式
   - 需要 `tool_use_id` 引用

3. **重写消息格式**:
```python
# 用户消息
{"role": "user", "content": [{"type": "text", "text": "..."}]}

# 助手消息（带工具调用）
{
  "role": "assistant", 
  "content": [
    {"type": "text", "text": "..."},
    {"type": "tool_use", "id": "tool_1", "name": "write_draft", "input": {...}}
  ]
}

# 工具结果消息
{"role": "user", "content": [{"type": "tool_result", "tool_use_id": "tool_1", "content": "..."}]}
```

### 步骤 3: 修改 `MessageHistory` 类

支持 Anthropic 格式的消息类型：
- `type: "text"`
- `type: "tool_use"`
- `type: "tool_result"`

### 步骤 4: 修改 ReAct 循环 `src/core/react.py`

从 `tool_use` 块中提取工具调用：
```python
# 从 Anthropic 格式响应中提取
for block in response.content:
    if block.type == "tool_use":
        tool_name = block.name
        tool_args = block.input
```

---

## 预期结果

- ReAct 循环正常工作
- 工具调用被正确解析和执行
- 多轮对话保持连贯
