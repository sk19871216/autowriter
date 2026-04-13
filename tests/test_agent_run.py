"""测试 WritingAgent 运行

使用示例：
python tests/test_agent_run.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_direct_write():
    """直接测试写作功能（绕过 ReAct 循环）"""
    from autowriter.src.llm.client import LLMClient

    client = LLMClient()

    prompt = """你是专业的小说作家。

请根据以下素材创作小说章节开头：

帮我写一个开头，主角叫林清瑶，是一个身负血仇的女剑客，场景在雨夜的破庙

写作要求：
1. 描写生动细腻，营造氛围
2. 符合古龙式冷峻风格
3. 注重人物刻画和心理描写
4. 短句为主，环境渲染意境
5. 直接输出小说内容，不需要任何说明

小说内容："""

    print("=" * 60)
    print("直接写作测试")
    print("=" * 60)

    message = client.create_message(
        system="你是专业的小说作家。",
        user_message="根据以下素材创作：主角叫林清瑶，是一个身负血仇的女剑客，场景在雨夜的破庙。请描写生动，符合古龙式冷峻风格。",
        max_tokens=2000
    )

    result = client.parse_response(message)

    print("-" * 60)
    print("生成结果:")
    print("-" * 60)
    print(result["content"])
    print("=" * 60)

    return result


def test_full_react():
    """测试完整的 ReAct 循环"""
    from autowriter.src.core.agent import create_agent

    agent = create_agent("my_novel")

    result = agent.process_instruction(
        "帮我写一个开头，主角叫林清瑶，是一个身负血仇的女剑客，场景在雨夜的破庙"
    )

    print("=" * 60)
    print("完整 ReAct 循环测试")
    print("=" * 60)
    print(f"成功: {result['success']}")
    print(f"类型: {result['task_type']}")
    print(f"\n内容:\n{result['content']}")
    if result['history']:
        print(f"\n历史记录数: {len(result['history'])}")
    if result['error']:
        print(f"\n错误: {result['error']}")
    print("=" * 60)

    return result


if __name__ == "__main__":
    print("开始测试 WritingAgent...\n")

    print("\n" + "=" * 60)
    print("[测试1] 直接写作测试（推荐先运行这个）")
    print("=" * 60)
    test_direct_write()

    print("\n\n" + "=" * 60)
    print("[测试2] 完整 ReAct 循环测试（需要 API Key）")
    print("=" * 60)
    test_full_react()
