"""
Example 03: Built-in Tools

The Claude Agent SDK comes with built-in tools that the model can use.
These tools let the model interact with your filesystem and run commands.

Available built-in tools:
- Read     — read any file in the working directory
- Write    — create new files
- Edit     — make precise edits to existing files
- Bash     — run terminal commands, scripts, git operations
- Glob     — find files by pattern (e.g. "**/*.py", "src/**/*.ts")
- Grep     — search file contents with regex
- WebSearch — search the web for current information
- WebFetch — fetch and parse web page content

This example uses Glob + Read + Bash together — a common combination
for code analysis tasks.

Concepts introduced:
- allowed_tools — which tools the model can use
- permission_mode — "acceptEdits" auto-approves file modifications
- Tool combination — the model chains multiple tools in one task
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock, ToolUseBlock


async def main():
    """
    Ask Claude to find all Python files and count lines in each.
    
    The model will likely:
    1. Use Glob to find *.py files
    2. Use Read to read each file (or Bash with wc -l)
    3. Summarize the results
    
    Watch how it chains multiple tool calls — each one gives it more
    information to work with.
    """
    async for msg in query(
        prompt="Find all Python files in the current directory and tell me how many lines each has",
        options=ClaudeAgentOptions(
            allowed_tools=["Glob", "Read", "Bash"],
            permission_mode="acceptEdits",  # Auto-approve file operations
        ),
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(block.text, end="", flush=True)
                elif isinstance(block, ToolUseBlock):
                    # Show each tool call as it happens
                    print(f"\n  → {block.name}({block.arguments})", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
