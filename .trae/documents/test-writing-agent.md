# 测试计划：运行 WritingAgent 写作测试

## 目标

使用用户提供的素材「帮我写一个开头，主角叫林清瑶，是一个身负血仇的女剑客，场景在雨夜的破庙」，在 WritingAgent 代码中运行测试。

## 问题分析

### 1. 依赖缺失
- `requests` 库未在 `pyproject.toml` 中列出

### 2. API 配置
- 需要获取 TRAE 的 API Key（可能通过环境变量或配置读取）
- 需要确认 API 端点格式

### 3. 工具实现不完整
- 当前 `_tool_write_draft` 只返回占位符
- 需要让它真正调用 LLM 生成内容

### 4. 测试入口
- 需要创建简单的测试脚本

---

## 实施步骤

### 步骤 1: 添加缺失依赖
- 在 `pyproject.toml` 中添加 `requests` 依赖

### 步骤 2: 创建测试脚本 `tests/test_agent_run.py`
```python
"""测试 WritingAgent 运行"""
from autowriter.src.core.agent import create_agent

def test_write_opening():
    agent = create_agent("my_novel")
    
    result = agent.process_instruction(
        "帮我写一个开头，主角叫林清瑶，是一个身负血仇的女剑客，场景在雨夜的破庙"
    )
    
    print("=== 测试结果 ===")
    print(f"成功: {result['success']}")
    print(f"类型: {result['task_type']}")
    print(f"内容: {result['content']}")
    if result['history']:
        print(f"历史: {result['history']}")
    if result['error']:
        print(f"错误: {result['error']}")
```

### 步骤 3: 实现真正的 write_draft 工具
修改 `_tool_write_draft` 方法，使其调用 LLM 生成内容：

```python
def _tool_write_draft(self, chapter: int, outline: str) -> str:
    """工具：写章节草稿"""
    prompt = f"""请根据以下大纲创作小说章节：

大纲：{outline}

要求：
1. 描写生动细腻
2. 符合古龙式冷峻风格
3. 注重人物刻画

请直接输出小说内容，不要有其他说明。
"""
    response = self.llm_client.call(prompt, temperature=0.8)
    return response.content or "[生成失败]"
```

### 步骤 4: 处理 API 认证
- 检测是否配置了 API Key
- 如果没有，尝试从 TRAE 配置读取或提示用户

### 步骤 5: 运行测试
```bash
python -m pytest tests/test_agent_run.py -v
```

---

## 预期输出

```
=== 测试结果 ===
成功: True
类型: write
内容: [LLM 生成的小说开头内容]
```

---

## 风险与备选方案

| 风险 | 备选方案 |
|------|----------|
| API Key 不可用 | 使用 mock LLM 返回预设内容 |
| 网络请求失败 | 添加重试机制和超时处理 |
| 生成内容不符合预期 | 调整 temperature 和 prompt |
