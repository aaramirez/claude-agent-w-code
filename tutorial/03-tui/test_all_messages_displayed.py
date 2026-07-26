"""
Test: Verify that ALL SDK messages are captured and would be displayed.

This script runs a query through the Claude Agent SDK and logs every message
received. It then compares against what the TUI formatter would display to
ensure nothing is lost.

Usage:
    python test_all_messages_displayed.py
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from message_formatter import (
    format_user_input,
    format_assistant_text,
    format_tool_use,
    format_tool_result,
    format_thinking,
    format_result_message,
    format_system_message,
    format_error,
    format_separator,
    format_debug_message,
    format_debug_raw,
)


class MessageTracker:
    """Tracks all messages received from the SDK and what would be displayed."""

    def __init__(self):
        self.all_messages = []
        self.displayed_items = []
        self.missing_items = []

    def log_raw_message(self, msg, index):
        """Log a raw SDK message."""
        self.all_messages.append({
            "index": index,
            "type": type(msg).__name__,
            "repr": repr(msg),
            "timestamp": datetime.now().isoformat(),
        })

    def log_display(self, item_type, item_desc, renderable):
        """Log an item that would be displayed in the TUI."""
        self.displayed_items.append({
            "type": item_type,
            "description": item_desc,
            "has_content": renderable is not None,
            "content_length": len(str(renderable)) if renderable else 0,
        })

    def log_missing(self, item_type, item_desc):
        """Log a missing item that should be displayed."""
        self.missing_items.append({
            "type": item_type,
            "description": item_desc,
        })

    def print_report(self):
        """Print the full test report."""
        print("\n" + "=" * 70)
        print("MESSAGE DISPLAY TEST REPORT")
        print("=" * 70)

        print(f"\nTotal SDK messages received: {len(self.all_messages)}")
        print(f"Total items displayed:       {len(self.displayed_items)}")
        print(f"Missing items:               {len(self.missing_items)}")

        print("\n--- ALL SDK MESSAGES ---")
        for msg in self.all_messages:
            print(f"  [{msg['index']:3d}] {msg['type']:20s} | {msg['repr'][:100]}")

        print("\n--- ITEMS DISPLAYED IN TUI ---")
        for item in self.displayed_items:
            print(f"  {item['type']:20s} | {item['description'][:60]:60s} | content_len={item['content_length']}")

        if self.missing_items:
            print("\n--- MISSING ITEMS (NOT DISPLAYED) ---")
            for item in self.missing_items:
                print(f"  {item['type']:20s} | {item['description']}")
            print(f"\n  FAILED: {len(self.missing_items)} items would NOT be displayed!")
        else:
            print("\n  PASSED: All SDK messages would be displayed in the TUI.")

        # Check for empty formatters
        print("\n--- FORMATTER VALIDATION ---")
        test_cases = [
            ("format_user_input", format_user_input("test prompt")),
            ("format_assistant_text", format_assistant_text("test response")),
            ("format_tool_use", format_tool_use("Read", {"file_path": "/test"})),
            ("format_tool_result", format_tool_result("test result content")),
            ("format_result_message", format_result_message(stop_reason="end_turn", num_turns=1, cost_usd=0.001)),
            ("format_system_message", format_system_message("init", {"session_id": "abc123"})),
            ("format_error", format_error("test error")),
            ("format_separator", format_separator("Test")),
            ("format_debug_message", format_debug_message(type('MockMsg', (), {'content': [], 'stop_reason': None, 'total_cost_usd': None, 'num_turns': None, 'subtype': None, 'data': None})())),
            ("format_debug_raw", format_debug_raw(type('MockMsg', (), {'content': [], 'stop_reason': None, 'total_cost_usd': None, 'num_turns': None, 'subtype': None, 'data': None})())),
        ]

        all_ok = True
        for name, result in test_cases:
            has_content = result is not None and len(str(result)) > 0
            status = "OK" if has_content else "EMPTY"
            if not has_content:
                all_ok = False
            print(f"  {name:30s} | {status:5s} | len={len(str(result)) if result else 0}")

        if all_ok:
            print("\n  PASSED: All formatters produce non-empty output.")
        else:
            print("\n  FAILED: Some formatters produce empty output!")

        print("\n" + "=" * 70)
        return len(self.missing_items) == 0 and all_ok


async def test_sdk_messages():
    """Run a test query and verify all messages are captured."""
    try:
        from claude_agent_sdk import (
            query,
            ClaudeAgentOptions,
            AssistantMessage,
            TextBlock,
            ToolUseBlock,
            ToolResultBlock,
            ThinkingBlock,
            ResultMessage,
            SystemMessage,
        )
    except ImportError:
        print("ERROR: claude-agent-sdk not installed. Run: pip install claude-agent-sdk")
        print("Also ensure ANTHROPIC_API_KEY is set.")
        return False

    tracker = MessageTracker()
    index = 0

    print("Running test query: 'What is 2 + 2? Respond with just the number.'")
    print("This should produce a simple text response with no tools.\n")

    try:
        async for msg in query(
            prompt="What is 2 + 2? Respond with just the number.",
            options=ClaudeAgentOptions(),
        ):
            tracker.log_raw_message(msg, index)

            # Check what the TUI would display for this message
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        renderable = format_assistant_text(block.text)
                        tracker.log_display("AssistantText", f"text={block.text[:50]}", renderable)
                    elif isinstance(block, ToolUseBlock):
                        renderable = format_tool_use(block.name, block.input)
                        tracker.log_display("ToolUse", f"{block.name}", renderable)
                    elif isinstance(block, ToolResultBlock):
                        content = getattr(block, "content", None) or getattr(block, "output", "")
                        renderable = format_tool_result(content)
                        tracker.log_display("ToolResult", f"content_len={len(str(content))}", renderable)
                    elif isinstance(block, ThinkingBlock):
                        renderable = format_thinking(block.thinking)
                        tracker.log_display("Thinking", f"len={len(block.thinking)}", renderable)
                    else:
                        tracker.log_display("UnknownBlock", type(block).__name__, None)
                        tracker.log_missing("UnknownBlock", type(block).__name__)

            elif isinstance(msg, ResultMessage):
                renderable = format_result_message(
                    stop_reason=msg.stop_reason,
                    num_turns=msg.num_turns,
                    cost_usd=msg.total_cost_usd,
                )
                tracker.log_display("ResultMessage", f"stop={msg.stop_reason}", renderable)

            elif isinstance(msg, SystemMessage):
                renderable = format_system_message(
                    getattr(msg, "subtype", "unknown"),
                    getattr(msg, "data", None),
                )
                tracker.log_display("SystemMessage", f"subtype={getattr(msg, 'subtype', '?')}", renderable)

            else:
                # Unknown type — would be displayed as system message
                renderable = format_system_message(
                    f"msg:{type(msg).__name__}",
                    {"repr": repr(msg)},
                )
                tracker.log_display("UnknownMsg", type(msg).__name__, renderable)

            index += 1

    except Exception as e:
        print(f"ERROR during query: {e}")
        tracker.log_missing("Exception", str(e))

    return tracker.print_report()


async def test_tool_use_messages():
    """Run a test query that uses tools and verify all messages are captured."""
    try:
        from claude_agent_sdk import (
            query,
            ClaudeAgentOptions,
            AssistantMessage,
            TextBlock,
            ToolUseBlock,
            ToolResultBlock,
            ThinkingBlock,
            ResultMessage,
            SystemMessage,
        )
    except ImportError:
        print("ERROR: claude-agent-sdk not installed.")
        return False

    tracker = MessageTracker()
    index = 0

    print("\n\nRunning tool-use test query: 'Read the file README.md in the current directory'")
    print("This should produce tool calls (Read/Glob) and results.\n")

    try:
        async for msg in query(
            prompt="Read the file README.md in the current directory",
            options=ClaudeAgentOptions(
                allowed_tools=["Read", "Glob", "Grep"],
                permission_mode="acceptEdits",
            ),
        ):
            tracker.log_raw_message(msg, index)

            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        renderable = format_assistant_text(block.text)
                        tracker.log_display("AssistantText", f"text={block.text[:50]}", renderable)
                    elif isinstance(block, ToolUseBlock):
                        renderable = format_tool_use(block.name, block.input)
                        tracker.log_display("ToolUse", f"{block.name}", renderable)
                    elif isinstance(block, ToolResultBlock):
                        content = getattr(block, "content", None) or getattr(block, "output", "")
                        renderable = format_tool_result(content)
                        tracker.log_display("ToolResult", f"content_len={len(str(content))}", renderable)
                    elif isinstance(block, ThinkingBlock):
                        renderable = format_thinking(block.thinking)
                        tracker.log_display("Thinking", f"len={len(block.thinking)}", renderable)
                    else:
                        tracker.log_display("UnknownBlock", type(block).__name__, None)
                        tracker.log_missing("UnknownBlock", type(block).__name__)

            elif isinstance(msg, ResultMessage):
                renderable = format_result_message(
                    stop_reason=msg.stop_reason,
                    num_turns=msg.num_turns,
                    cost_usd=msg.total_cost_usd,
                )
                tracker.log_display("ResultMessage", f"stop={msg.stop_reason}", renderable)

            elif isinstance(msg, SystemMessage):
                renderable = format_system_message(
                    getattr(msg, "subtype", "unknown"),
                    getattr(msg, "data", None),
                )
                tracker.log_display("SystemMessage", f"subtype={getattr(msg, 'subtype', '?')}", renderable)

            else:
                renderable = format_system_message(
                    f"msg:{type(msg).__name__}",
                    {"repr": repr(msg)},
                )
                tracker.log_display("UnknownMsg", type(msg).__name__, renderable)

            index += 1

    except Exception as e:
        print(f"ERROR during query: {e}")
        tracker.log_missing("Exception", str(e))

    return tracker.print_report()


async def main():
    print("=" * 70)
    print("TUI MESSAGE DISPLAY TEST SUITE")
    print("=" * 70)

    result1 = await test_sdk_messages()
    result2 = await test_tool_use_messages()

    print("\n" + "=" * 70)
    if result1 and result2:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED — check report above")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
