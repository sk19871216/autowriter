# 修复计划：使用官方 Anthropic SDK

## 问题分析

用户指出：为什么不直接使用官网上推荐的 `anthropic` Python 包，而是要自己写 HTTP 客户端？

**答案**：应该用官方 SDK！这样可以：
1. 自动处理 URL 拼接（`base_url` + `/messages`）
2. 自动处理消息格式（`content: [{"type": "text"}]`）
3. 自动处理工具调用（`tool_use` / `tool_result`）
4. 更可靠，减少手动解析的错误

---

## 修复方案

### 步骤 1: 安装 anthropic SDK ✅

```bash
pip install anthropic
```

### 步骤 2: 重写 LLMClient 使用 SDK ✅

完全按照官方文档：
```python
from anthropic import Anthropic

client = Anthropic(
    api_key=api_key,
    base_url="https://api.minimaxi.com/anthropic"
)

message = client.messages.create(
    model="MiniMax-M2.7",
    max_tokens=1000,
    system="You are a helpful assistant.",
    messages=[
        {"role": "user", "content": [{"type": "text", "text": "..."}]}
    ]
)

for block in message.content:
    if block.type == "text":
        print(block.text)
```

### 步骤 3: 更新 pyproject.toml ✅

```toml
dependencies = [
    "anthropic>=0.18.0",
]
```

---

## 验证结果

- ✅ 直接写作测试成功
- ✅ ReAct 循环正确执行工具调用
- ✅ MiniMax M2.7 生成完整章节内容
- ✅ 代码更简洁可靠
