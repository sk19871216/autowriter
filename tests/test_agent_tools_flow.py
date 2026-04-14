"""测试 Agent 工具调用流程"""

import logging
import json

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

from autowriter.src.core.agent import WritingAgent

def test_agent_tools():
    agent = WritingAgent(project_path="my_novel")

    user_input = "陈华一觉醒来，回到了18岁父母出事的前一天，这一世，悲剧一定不会发生。"

    print("=" * 60)
    print(f"用户输入: {user_input}")
    print("=" * 60)

    result = agent.process_instruction(user_input)

    print("\n" + "=" * 60)
    print("执行结果:")
    print("=" * 60)

    if result.get("history"):
        for i, step in enumerate(result["history"]):
            state = step.get("state", "UNKNOWN")
            print(f"\n【步骤 {i+1}】状态: {state}")

            if state == "THINKING":
                thought = step.get("thought", "")
                print(f"  思考: {thought[:200]}..." if len(thought) > 200 else f"  思考: {thought}")
                if step.get("action"):
                    if isinstance(step["action"], dict):
                        print(f"  行动: 调用工具 {step['action'].get('tool', 'unknown')}")
                        print(f"  参数: {json.dumps(step['action'].get('args', {}), ensure_ascii=False)}")
                    else:
                        print(f"  行动: {step['action']}")

            elif state == "ACTION":
                print(f"  工具: {step.get('tool', 'unknown')}")
                print(f"  参数: {json.dumps(step.get('args', {}), ensure_ascii=False)}")
                if step.get("error"):
                    print(f"  错误: {step['error']}")

            elif state == "OBSERVING":
                obs = step.get("observation", "")
                print(f"  观察: {obs[:300]}..." if len(obs) > 300 else f"  观察: {obs}")

    print("\n" + "=" * 60)
    print("最终输出:")
    print("=" * 60)
    content = result.get("content", "")
    print(content[:1000] + "..." if len(content) > 1000 else content)

    print("\n" + "=" * 60)
    print("工具调用统计:")
    print("=" * 60)

    tools_used = {}
    for step in result.get("history", []):
        if step.get("state") == "ACTION" and step.get("tool"):
            tool_name = step["tool"]
            tools_used[tool_name] = tools_used.get(tool_name, 0) + 1

    for tool, count in sorted(tools_used.items(), key=lambda x: -x[1]):
        print(f"  {tool}: {count} 次")

    return result

if __name__ == "__main__":
    test_agent_tools()
