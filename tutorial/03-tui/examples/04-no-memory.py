"""
Example 04: No Memory — AI Models Have No Memory (TUI)

This is the KEY example that demonstrates a fundamental truth about AI models:

  AI MODELS HAVE NO PERSISTENT MEMORY.

Each API call is STATELESS. The model only sees what you send it in that
specific request. It does NOT remember previous conversations, previous
prompts, or anything from the past unless you explicitly include that
information in the request.

This example shows TWO scenarios:

  PART 1 — WITHOUT MEMORY (standalone query calls):
    Query 1: "My name is Carlos and I'm building a weather app"
    Query 2: "What's my name and what am I building?"
    Result: Claude DOESN'T KNOW. Each query is independent.

  PART 2 — WITH MEMORY (session resume):
    Query 1: "My name is Carlos and I'm building a weather app"
    Query 2 (resume session): "What's my name and what am I building?"
    Result: Claude REMEMBERS. Session preserves context.

The difference is clear: without explicit session management,
every conversation starts from zero.

Run:
    cd tutorial/03-tui
    pip install -r requirements.txt
    python examples/04-no-memory.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.text import Text

from agent_tui import AgentTuiApp
from message_formatter import (
    format_separator,
    format_user_input,
    format_assistant_text,
    format_system_message,
    format_result_message,
    format_error,
)
from debug_panel import DebugPanel


# ── No-Memory TUI ─────────────────────────────────────────────────────

class NoMemoryTuiApp(AgentTuiApp):
    """
    Custom TUI that demonstrates the no-memory problem.

    Overrides the default agent behavior to run a two-part demonstration:
    1. Standalone queries (no memory)
    2. Session-resumed queries (with memory)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._demo_phase = 0  # 0=not started, 1=part1, 2=part2

    async def on_input_submitted(self, event):
        """Override to run the demo instead of free-form chat."""
        text = event.value.strip()
        event.input.value = ""

        if not text:
            return

        # Allow slash commands
        if text.startswith("/"):
            self._handle_command(text)
            return

        # First input triggers the demo
        if self._demo_phase == 0:
            self._demo_phase = 1
            self.run_worker(self._run_demo(), thread=True, exclusive=True, group="demo")
        else:
            # After demo, allow free chat
            await self._send_to_agent(text)

    async def _run_demo(self):
        """Run the two-part no-memory demonstration."""
        from claude_agent_sdk import (
            query,
            ClaudeAgentOptions,
            ClaudeSDKClient,
            AssistantMessage,
            TextBlock,
            ResultMessage,
            SystemMessage,
        )

        console_clear = lambda: self.call_from_thread(
            self.query_one("#conversation", __import__("textual.widgets", fromlist=["RichLog"]).RichLog).clear
        )

        # ── PART 1: WITHOUT MEMORY ────────────────────────────────────
        self.call_from_thread(
            self._write_to_console,
            format_separator("PART 1: WITHOUT MEMORY (standalone queries)"),
            Text(
                "  Each query is INDEPENDENT. The model has NO memory of previous conversations.\n"
                "  Without explicit history, every API call starts from zero.\n\n",
                style="italic yellow",
            ),
        )

        # Query 1: Establish context
        self.call_from_thread(
            self._write_to_console,
            format_separator("Query 1"),
            format_user_input("My name is Carlos and I'm building a weather app"),
        )

        try:
            async for msg in query(
                prompt="My name is Carlos and I'm building a weather app. Acknowledge this.",
                options=ClaudeAgentOptions(allowed_tools=[]),
            ):
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            self.call_from_thread(
                                self._write_to_console,
                                format_assistant_text(block.text),
                            )
                elif isinstance(msg, ResultMessage):
                    self.call_from_thread(
                        self._write_to_console,
                        format_result_message(
                            stop_reason=msg.stop_reason,
                            num_turns=msg.num_turns,
                            cost_usd=msg.total_cost_usd,
                        ),
                    )
        except Exception as e:
            self.call_from_thread(
                self._write_to_console,
                format_error(f"Part 1, Query 1 failed: {e}"),
            )

        # Query 2: Ask what it remembers (it won't remember!)
        self.call_from_thread(
            self._write_to_console,
            format_separator("Query 2 (separate API call — no session)"),
            format_user_input("What's my name and what am I building?"),
        )

        try:
            async for msg in query(
                prompt="What's my name and what am I building?",
                options=ClaudeAgentOptions(allowed_tools=[]),
            ):
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            self.call_from_thread(
                                self._write_to_console,
                                format_assistant_text(block.text),
                            )
                elif isinstance(msg, ResultMessage):
                    self.call_from_thread(
                        self._write_to_console,
                        format_result_message(
                            stop_reason=msg.stop_reason,
                            num_turns=msg.num_turns,
                            cost_usd=msg.total_cost_usd,
                        ),
                    )
        except Exception as e:
            self.call_from_thread(
                self._write_to_console,
                format_error(f"Part 1, Query 2 failed: {e}"),
            )

        # Verdict for Part 1
        self.call_from_thread(
            self._write_to_console,
            Text(
                "\n  RESULT: Claude doesn't remember! The model has NO memory across separate queries.\n"
                "  Each API call is stateless — it only sees what you send in THAT request.\n",
                style="bold red",
            ),
        )

        # ── PART 2: WITH MEMORY (session resume) ──────────────────────
        self.call_from_thread(
            self._write_to_console,
            format_separator("PART 2: WITH MEMORY (session resume)"),
            Text(
                "  Using session_id to RESUME the conversation. Claude remembers everything.\n"
                "  The session stores the full conversation history and replays it.\n\n",
                style="italic green",
            ),
        )

        session_id = None

        # Query 1: Establish context + capture session_id
        self.call_from_thread(
            self._write_to_console,
            format_separator("Query 1"),
            format_user_input("My name is Carlos and I'm building a weather app"),
        )

        try:
            async for msg in query(
                prompt="My name is Carlos and I'm building a weather app. Acknowledge this.",
                options=ClaudeAgentOptions(allowed_tools=[]),
            ):
                if isinstance(msg, SystemMessage):
                    if hasattr(msg, "subtype") and msg.subtype == "init":
                        if hasattr(msg, "data") and isinstance(msg.data, dict):
                            session_id = msg.data.get("session_id")
                            self.session_id = session_id
                            self.call_from_thread(
                                self._write_to_console,
                                format_system_message("init", msg.data),
                            )

                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            self.call_from_thread(
                                self._write_to_console,
                                format_assistant_text(block.text),
                            )
                elif isinstance(msg, ResultMessage):
                    self.call_from_thread(
                        self._write_to_console,
                        format_result_message(
                            stop_reason=msg.stop_reason,
                            num_turns=msg.num_turns,
                            cost_usd=msg.total_cost_usd,
                            session_id=session_id,
                        ),
                    )
        except Exception as e:
            self.call_from_thread(
                self._write_to_console,
                format_error(f"Part 2, Query 1 failed: {e}"),
            )

        if not session_id:
            self.call_from_thread(
                self._write_to_console,
                format_error("Failed to capture session_id. Cannot proceed with Part 2."),
            )
            self.call_from_thread(self._on_stream_complete)
            return

        # Query 2: Resume session and ask what it remembers
        self.call_from_thread(
            self._write_to_console,
            format_separator(f"Query 2 (resuming session {session_id[:12]}...)"),
            format_user_input("What's my name and what am I building?"),
        )

        try:
            async for msg in query(
                prompt="What's my name and what am I building?",
                options=ClaudeAgentOptions(
                    resume=session_id,
                    allowed_tools=[],
                ),
            ):
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            self.call_from_thread(
                                self._write_to_console,
                                format_assistant_text(block.text),
                            )
                elif isinstance(msg, ResultMessage):
                    self.call_from_thread(
                        self._write_to_console,
                        format_result_message(
                            stop_reason=msg.stop_reason,
                            num_turns=msg.num_turns,
                            cost_usd=msg.total_cost_usd,
                            session_id=session_id,
                        ),
                    )
        except Exception as e:
            self.call_from_thread(
                self._write_to_console,
                format_error(f"Part 2, Query 2 failed: {e}"),
            )

        # Verdict for Part 2
        self.call_from_thread(
            self._write_to_console,
            Text(
                "\n  RESULT: Claude remembers! Session resume preserves the full context.\n"
                "  The session_id stores the conversation history and replays it with each request.\n",
                style="bold green",
            ),
        )

        # ── Summary ───────────────────────────────────────────────────
        self.call_from_thread(
            self._write_to_console,
            format_separator("KEY TAKEAWAY"),
            Text(
                "  AI models are STATELESS by default.\n"
                "  They have NO memory between API calls.\n\n"
                "  To maintain context, you must explicitly:\n"
                "    1. Pass conversation history in each request (manual)\n"
                "    2. Use sessions (session_id + resume) (automatic)\n"
                "    3. Use ClaudeSDKClient which maintains context (automatic)\n\n"
                "  Without one of these, every conversation starts from zero.\n",
                style="bold white",
            ),
            format_separator(""),
            Text(
                "  Demo complete! You can now type prompts for free chat.\n"
                "  Use /debug to see raw SDK messages.\n\n",
                style="italic cyan",
            ),
        )

        self.call_from_thread(self._on_stream_complete)


def main():
    """
    Launch the no-memory demonstration TUI.

    Press Enter (or type anything) to start the demo.
    """
    app = NoMemoryTuiApp(
        instructions=(
            "This example runs a two-part demo automatically.\n"
            "  Press Enter (or type anything) to start.\n"
            "  After the demo, you can chat freely."
        ),
    )
    app.run()


if __name__ == "__main__":
    main()
