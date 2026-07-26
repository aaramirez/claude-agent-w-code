"""
Example 01: Hello Agent

The simplest possible agent. Sends a prompt to Claude and prints the response.

No tools are used — the model just generates text.

Concepts introduced:
- query() — the main entry point for sending prompts
- ClaudeAgentOptions — configuration for the agent
- allowed_tools — which tools the model can use (empty = none)
- Async iteration — processing streamed messages
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    """
    Send a simple prompt and print every message the model sends back.
    
    With no tools allowed, the model can only generate text.
    It cannot read files, run commands, or access the internet.
    """
    async for msg in query(
        prompt="Say hello in 3 languages with a brief translation",
        options=ClaudeAgentOptions(
            allowed_tools=[]  # No tools — text-only response
        ),
    ):
        # Messages stream in as the model generates them.
        # With no tools, you'll get AssistantMessage with TextBlock(s).
        print(msg)


if __name__ == "__main__":
    asyncio.run(main())
