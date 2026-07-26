"""
Example 09: Sessions

Sessions let you save and resume the agent's context across multiple
queries. Claude remembers everything: files read, analysis done,
conversation history, and tool results.

Why use sessions?
- Long-running tasks: break a big task into smaller steps
- Interactive workflows: user reviews between steps
- Context persistence: Claude remembers what it learned earlier
- Forking: explore different approaches from the same starting point

Concepts introduced:
- session_id — unique identifier for a conversation
- SystemMessage with subtype="init" — contains the session_id
- resume — continue an existing session
- fork_session — branch from an existing session
"""

import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    SystemMessage,
    ResultMessage,
)


async def main():
    """
    Two-step workflow:
    
    Step 1: Ask Claude to analyze auth.py and remember the issues
            Capture the session_id from the init message
    
    Step 2: Resume the session and ask Claude to fix the issues
            Claude remembers everything from step 1
    
    Without sessions, step 2 would have no context — Claude wouldn't
    know what issues were found. With sessions, it remembers everything.
    """
    session_id = None

    # ── Step 1: Analyze the code ─────────────────────────────────────
    print("=" * 50)
    print("STEP 1: Analyze auth.py")
    print("=" * 50)

    async for msg in query(
        prompt=(
            "Read the auth-related Python files in this directory. "
            "Identify all security issues and best practice violations. "
            "Remember what you find — I'll ask you to fix them next."
        ),
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep"],
        ),
    ):
        # Capture the session_id from the init message
        if isinstance(msg, SystemMessage) and msg.subtype == "init":
            session_id = msg.data["session_id"]
            print(f"Session started: {session_id}")

        if isinstance(msg, ResultMessage):
            print(f"\nAnalysis complete. {msg.num_turns} turns, ${msg.total_cost_usd:.4f}")

    if not session_id:
        print("ERROR: No session_id captured")
        return

    # ── Step 2: Fix the issues (resume session) ─────────────────────
    print("\n" + "=" * 50)
    print("STEP 2: Fix the issues (resuming session)")
    print("=" * 50)

    async for msg in query(
        prompt="Now fix all the security issues you found. Make the minimal necessary changes.",
        options=ClaudeAgentOptions(
            resume=session_id,              # Resume the previous session
            allowed_tools=["Read", "Edit"], # Can read and edit files
        ),
    ):
        if isinstance(msg, ResultMessage):
            print(f"\nFix complete. {msg.num_turns} turns, ${msg.total_cost_usd:.4f}")
            print(f"Stop reason: {msg.stop_reason}")


if __name__ == "__main__":
    asyncio.run(main())
