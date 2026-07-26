"""
Example 05: Bidirectional Streaming

ClaudeSDKClient gives you more control than query(). With it, you can:
- Maintain a persistent session across multiple queries
- Observe each message as it arrives
- Send follow-up prompts in the same context

This is the difference:
- query() = fire-and-forget, you just see messages stream by
- ClaudeSDKClient = interactive session, you control the conversation

Concepts introduced:
- ClaudeSDKClient — the interactive client
- connect() — start a session with an initial prompt
- query() — send additional prompts in the same session
- receive_response() — async iterator over messages
- disconnect() — end the session
- Session persistence — Claude remembers everything from prior queries
"""

import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
)


async def main():
    """
    Start an interactive session with Claude.
    
    1. Connect with an initial prompt (lists files in the directory)
    2. Send a follow-up (reads the main file)
    3. Send another follow-up (explains what it found)
    
    All three queries share the same context — Claude remembers everything.
    """
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep"],
        permission_mode="acceptEdits",
    )

    async with ClaudeSDKClient(options) as client:
        # ── First query ──────────────────────────────────────────────
        print("=" * 50)
        print("QUERY 1: List files in the directory")
        print("=" * 50)

        await client.connect(prompt="What files are in the current directory? List them all.")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"\nClaude: {block.text}")
                    elif isinstance(block, ToolUseBlock):
                        print(f"  → {block.name}({block.arguments})")

        # ── Second query (same session) ──────────────────────────────
        print("\n" + "=" * 50)
        print("QUERY 2: Read the main file")
        print("=" * 50)

        await client.query("Now read the first Python file you found and explain what it does")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"\nClaude: {block.text}")
                    elif isinstance(block, ToolUseBlock):
                        print(f"  → {block.name}({block.arguments})")

        # ── Third query (same session) ───────────────────────────────
        print("\n" + "=" * 50)
        print("QUERY 3: Summarize everything")
        print("=" * 50)

        await client.query("Based on everything you've seen, give me a brief summary of this project")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"\nClaude: {block.text}")


if __name__ == "__main__":
    asyncio.run(main())
