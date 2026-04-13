"""测试 agent 的记忆检索和工作流程 - 带调试信息"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autowriter.src.core.agent import WritingAgent


def main():
    print("=" * 60)
    print("测试：分层记忆系统 - Agent 工作流（调试版）")
    print("=" * 60)

    agent = WritingAgent(project_path="my_novel")

    print("\n📋 初始状态：加载记忆索引")
    full_index = agent.memory_retriever.get_full_index()
    print(f"【记忆索引】\n{full_index}")

    print("\n" + "=" * 60)
    print("🔍 测试检索功能")
    print("=" * 60)

    query = "林清瑶"
    print(f"\n调用 search('{query}'):")
    results = agent.memory_retriever.index_layer.search(query, top_k=3)
    for entry, score in results:
        print(f"  - [{entry.entry_type}] {entry.name} | {entry.description} | {entry.anchor} (score={score:.3f})")

    print(f"\n调用 retrieve('{query}'):")
    result = agent.memory_retriever.retrieve(query)
    print(f"  结果: {result[:200]}..." if len(result) > 200 else f"  结果: {result}")

    print("\n" + "=" * 60)
    print("用户指令：写一段林清瑶和李慕白在破庙对话的场景")
    print("=" * 60)

    print("\n🔍 第一步：Agent 检索角色记忆")

    print("\n调用工具: query_memory")
    print('参数: {"query": "林清瑶"}')
    result1 = agent._tool_query_memory("林清瑶")
    print(f"👀 观察结果:\n{result1}")

    print("\n调用工具: query_memory")
    print('参数: {"query": "李慕白"}')
    result2 = agent._tool_query_memory("李慕白")
    print(f"👀 观察结果:\n{result2}")

    print("\n调用工具: query_memory")
    print('参数: {"query": "破庙"}')
    result3 = agent._tool_query_memory("破庙")
    print(f"👀 观察结果:\n{result3}")

    print("\n" + "=" * 60)
    print("✍️ 第二步：生成对话场景")
    print("=" * 60)

    outline = "林清瑶和李慕白在破庙中相遇，进行一段对话。林清瑶性格寡言，李慕白阳光正直。"

    print("\n调用工具: write_draft")
    print(f'参数: {{"chapter": 1, "outline": "{outline}"}}')

    draft = agent._tool_write_draft(chapter=1, outline=outline)

    if hasattr(draft, '__len__') and len(draft) > 100:
        if 'ThinkingBlock' in str(type(draft)) or 'TextBlock' in str(type(draft)):
            draft_text = str(draft)
        else:
            draft_text = draft
    else:
        draft_text = draft

    print(f"\n📝 生成结果:\n{draft_text[:1500]}..." if len(str(draft_text)) > 1500 else f"\n📝 生成结果:\n{draft_text}")

    print("\n" + "=" * 60)
    print("✅ 工作流完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
