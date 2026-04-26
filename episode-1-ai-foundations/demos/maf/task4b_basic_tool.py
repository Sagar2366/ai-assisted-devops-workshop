#!/usr/bin/env python3
"""
Task 4b: Basic Tool Use — Pod Health Checker — MAF (Semantic Kernel)
See the model DECIDE to call a tool — the core of what makes an agent.
AI-Assisted DevOps Workshop | Episode 1 | Sagar Utekar

Prerequisites:
  export OPENAI_API_KEY="your-key-here"
  pip install semantic-kernel
"""

import asyncio
import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.functions import kernel_function
from semantic_kernel.contents.chat_history import ChatHistory

POD_STATUS_DB = {
    "monitoring": """NAME                          READY   STATUS             RESTARTS   AGE
prometheus-server-0            1/1     Running            0          7d
grafana-6b8c4d9f-n3k8p        1/1     Running            0          7d
alertmanager-0                 0/1     CrashLoopBackOff   5          2d
node-exporter-x4m9v            1/1     Running            0          7d"""
}


class K8sPlugin:
    # TODO 1: Decorate this function so Semantic Kernel registers it as a tool
    @kernel_function(name="check_pod_status", description="Check Kubernetes pod status in a namespace")
    def check_pod_status(self, namespace: str) -> str:
        """Check pod status in the given namespace."""
        print(f"\n  [TOOL CALLED] check_pod_status(namespace={namespace})")
        result = POD_STATUS_DB.get(namespace, f"No pods in '{namespace}'")
        print(f"  [TOOL RESULT]\n{result}\n")
        return ___  # TODO: Use result


async def run():
    print("=" * 65)
    print("Task 4b: Basic Tool Use — Pod Health Checker — MAF")
    print("=" * 65)

    kernel = Kernel()
    kernel.add_service(OpenAIChatCompletion(
        service_id="chat",
        ai_model_id="gpt-4o-mini",
        api_key=os.environ["OPENAI_API_KEY"]
    ))
    kernel.add_plugin(K8sPlugin(), plugin_name="k8s")

    settings = OpenAIChatPromptExecutionSettings(
        service_id="chat",
        max_tokens=1024,
        function_choice_behavior=FunctionChoiceBehavior.Auto()
    )

    history = ChatHistory()
    history.add_system_message("You are an SRE assistant. Use check_pod_status to inspect pods. Flag anything not Running.")

    query = "Are my pods healthy in the monitoring namespace?"
    print(f"\nQuery: {query}")
    print("-" * 40)

    history.add_user_message(query)
    chat = kernel.get_service("chat")
    response = await chat.get_chat_message_content(
        chat_history=history, settings=settings, kernel=kernel
    )
    print(f"Agent: {response.content}")

    print("\n" + "=" * 65)
    print("Key Learning: YOU defined the tool. The MODEL decided to call it.")
    print("That is the core of an agent — the model chooses when to act.")
    print("We go deep on tools in Episode 4.")
    print("=" * 65)

    print("\nTask 4b Complete!")
    print("Next: python3 demos/maf/task5_conversation_history.py")


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
