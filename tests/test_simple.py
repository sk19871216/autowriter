"""简单测试：完全按照官方文档使用 Anthropic SDK"""

import os
import anthropic


def test_simple():
    api_key = os.environ.get("MINIMAX_START")
    
    client = anthropic.Anthropic(
        api_key=api_key,
        base_url="https://api.minimaxi.com/anthropic"
    )
    
    print("测试发送消息（按照官方示例）...")
    print(f"API Key 已加载: {bool(api_key)}")
    
    message = client.messages.create(
        model="MiniMax-M2.7",
        max_tokens=1000,
        system="你是专业的小说作家。",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "用一句话描写雨夜破庙的场景。"
                    }
                ]
            }
        ]
    )
    
    print(f"响应类型: {type(message)}")
    print(f"stop_reason: {message.stop_reason}")
    
    for block in message.content:
        print(f"\nBlock type: {block.type}")
        if block.type == "text":
            print(f"Text: {block.text}")
        elif block.type == "thinking":
            print(f"Thinking: {block.thinking[:100]}...")


if __name__ == "__main__":
    test_simple()
