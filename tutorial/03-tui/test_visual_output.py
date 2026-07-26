"""
Visual Test: Shows EXACTLY what the TUI displays for a full conversation.

This runs a multi-turn conversation through the SDK and prints every
formatted message that would appear in the TUI, with colors.

Usage:
    cd tutorial/03-tui
    python test_visual_output.py
"""

import asyncio
import sys
import io
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.theme import Theme

sys.path.insert(0, str(Path(__file__).resolve().parent))

from message_formatter import (
    format_user_input,
    format_assistant_text,
    format_tool_use,
    format_tool_result,
    format_thinking,
    format_full_message,
    format_result_message,
    format_system_message,
    format_error,
    format_separator,
)

# Rich theme for the test output
theme = Theme({
    "user": "bold cyan",
    "model": "green",
    "tool": "yellow",
    "result": "dim white",
    "system": "blue",
    "error": "bold red",
    "done": "magenta",
    "debug": "italic gray50",
    "heading": "bold white on blue",
})

console = Console(theme=theme, highlight=False, force_terminal=True)


def display_renderable(renderable):
    """Display a Rich renderable to the console."""
    if renderable is not None:
        console.print(renderable)


async def run_conversation():
    """Run a full conversation and display everything."""
    try:
        from claude_agent_sdk import (
            query,
            ClaudeAgentOptions,
            AssistantMessage,
            UserMessage,
            TextBlock,
            ToolUseBlock,
            ToolResultBlock,
            ThinkingBlock,
            ResultMessage,
            SystemMessage,
        )
    except ImportError:
        console.print("[error]ERROR: claude-agent-sdk not installed.[/error]")
        return

    console.print(Panel(
        "This test shows EXACTLY what the TUI displays.\n"
        "Every message from the SDK is formatted and printed below.",
        title="[heading]Visual Test[/heading]",
        border_style="blue",
    ))

    # ── Turn 1: Simple question ────────────────────────────────────────
    console.print()
    display_renderable(format_separator("Turn 1"))
    display_renderable(format_user_input("What is 2 + 2? Then read the file pyproject.toml if it exists."))

    turn1_msgs = []
    async for msg in query(
        prompt="What is 2 + 2? Then read the file pyproject.toml if it exists.",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep"],
            permission_mode="acceptEdits",
        ),
    ):
        turn1_msgs.append(msg)
        display_renderable(format_full_message(type(msg).__name__, msg))

    # ── Turn 2: Follow-up (with memory via resume) ─────────────────────
    console.print()
    display_renderable(format_separator("Turn 2 (with memory — should remember turn 1)"))
    display_renderable(format_user_input("What was the answer to my math question?"))

    # Extract session_id from turn 1
    session_id = None
    for msg in turn1_msgs:
        if isinstance(msg, SystemMessage):
            if hasattr(msg, "subtype") and msg.subtype == "init":
                if hasattr(msg, "data") and isinstance(msg.data, dict):
                    session_id = msg.data.get("session_id")
        elif isinstance(msg, ResultMessage):
            result_session = getattr(msg, "session_id", None)
            if result_session:
                session_id = result_session

    if session_id:
        display_renderable(format_system_message("session", {"info": f"Resuming session {session_id[:16]}..."}))

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep"],
        permission_mode="acceptEdits",
    )
    if session_id:
        options = ClaudeAgentOptions(
            resume=session_id,
            allowed_tools=["Read", "Glob", "Grep"],
            permission_mode="acceptEdits",
        )

    async for msg in query(
        prompt="What was the answer to my math question?",
        options=options,
    ):
        display_renderable(format_full_message(type(msg).__name__, msg))

    # ── Summary ────────────────────────────────────────────────────────
    console.print()
    display_renderable(format_separator("Test Complete"))
    console.print(Panel(
        f"Total SDK messages turn 1: {len(turn1_msgs)}\n"
        "Everything above is what the TUI would display.\n"
        "If you see all content here but NOT in the TUI,\n"
        "the issue is in the RichLog widget, not the formatter.",
        title="[heading]Summary[/heading]",
        border_style="green",
    ))


if __name__ == "__main__":
    asyncio.run(run_conversation())
