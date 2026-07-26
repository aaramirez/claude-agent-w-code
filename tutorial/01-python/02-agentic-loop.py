"""
Example 02: The Agentic Loop in Action

This example lets you OBSERVE the agentic loop — the repeated cycle of
model response → tool call → execute → result → model response → ... → done.

We give the model access to the Read and Glob tools so it can inspect files.
Watch how it calls tools, gets results, and reasons about them.

Concepts introduced:
- AssistantMessage — the model's response
- TextBlock — plain text in the response
- ToolUseBlock — the model requesting a tool call (name + arguments)
- ToolResultBlock — your tool execution result (sent back automatically by SDK)
- ResultMessage — final metadata: stop_reason, cost, num_turns
- stop_reason — "tool_use" means the loop continues, "end_turn" means it's done
"""

import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage,
)


async def main():
    """
    Ask Claude to read the README file and summarize it.
    
    The model will:
    1. Decide it needs to read the file (generates a ToolUseBlock for "Read")
    2. The SDK executes the Read tool and appends the result
    3. The model reads the result and generates a summary (TextBlock)
    4. stop_reason becomes "end_turn" — loop ends
    """
    async for msg in query(
        prompt="Read the README.md in the current directory and give me a 2-sentence summary",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob"],  # Model can read files and search by pattern
        ),
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    # The model is talking — print its text
                    print(f"\n[TEXT] {block.text}")
                elif isinstance(block, ToolUseBlock):
                    # The model wants to call a tool — show what it's doing
                    print(f"\n[TOOL_USE] {block.name}({block.arguments})")
                    # The SDK will execute this tool and append the result automatically.
                    # You don't need to do anything here — just observe.

        elif isinstance(msg, ResultMessage):
            # The loop has ended — show final metadata
            print(f"\n{'='*50}")
            print(f"STOP REASON:    {msg.stop_reason}")
            print(f"TERMINAL:       {msg.terminal_reason}")
            print(f"NUM TURNS:      {msg.num_turns}")
            print(f"COST:           ${msg.total_cost_usd:.4f}" if msg.total_cost_usd else "COST: N/A")
            print(f"SESSION ID:     {msg.session_id}")
            print(f"{'='*50}")


if __name__ == "__main__":
    asyncio.run(main())
