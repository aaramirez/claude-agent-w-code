"""
Agent TUI — Interactive terminal interface for the Claude Agent SDK.

This module provides the main Textual application that wraps the Claude Agent SDK
into a beautiful, color-coded TUI. Everything the model sends or receives is
displayed on screen in a readable, didactic format.

Features:
  - User types prompts in an input field (auto-focused on mount)
  - All model interactions displayed with colors — NEVER truncated
  - Debug mode ON by default, /debug toggles it
  - Slash commands shown when typing /
  - Status bar: turn count, cost, debug state
  - RichLog is focusable — click or Tab to it, then use arrow keys to scroll

Usage:
  from agent_tui import AgentTuiApp

  app = AgentTuiApp(
      allowed_tools=["Read", "Glob"],
      permission_mode="acceptEdits",
  )
  app.run()
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Input, RichLog, Static
from textual.worker import get_current_worker

from debug_panel import DebugPanel
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

COMMANDS = {
    "/debug": "Toggle debug mode (shows raw SDK messages)",
    "/clear": "Clear conversation history",
    "/quit":  "Exit the TUI",
    "/help":  "Show available commands",
}


class AgentTuiApp(App):
    """
    Interactive TUI for Claude Agent SDK.

    Configure with allowed_tools, permission_mode, and other ClaudeAgentOptions.
    Subclass this to create specialized examples.
    """

    CSS_PATH = str(Path(__file__).resolve().parent / "styles.tcss")

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+c", "clear_conversation", "Clear", show=True),
        Binding("ctrl+d", "toggle_debug", "Debug", show=True),
        Binding("escape", "focus_input", "Input", show=True),
    ]

    TITLE = "Claude Agent TUI"

    def __init__(
        self,
        allowed_tools: list[str] | None = None,
        permission_mode: str | None = None,
        max_turns: int | None = None,
        max_budget_usd: float | None = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.allowed_tools = allowed_tools or []
        self.permission_mode = permission_mode
        self.max_turns = max_turns
        self.max_budget_usd = max_budget_usd

        # State
        self.debug_panel = DebugPanel(enabled=True)
        self.turn_count = 0
        self.total_cost = 0.0
        self.session_id: str | None = None
        self.is_streaming = False
        self._conversation_turn = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="conversation", highlight=False, markup=True, wrap=True, max_lines=None)
        yield Static(self._make_status(), id="status-bar")
        yield Input(placeholder="Type your prompt... (/help for commands)", id="input")
        yield Footer()

    def on_mount(self) -> None:
        """Focus the input field on mount and show welcome message."""
        self.query_one("#input", Input).focus()
        # Show welcome instructions
        self._write_to_console(format_separator("Claude Agent TUI"))
        self._write_to_console(format_system_message("welcome", {
            "info": (
                "Type a prompt and press Enter to send.\n"
                "  /help — show commands  |  Tab/Escape — switch focus\n"
                "  Click RichLog or press Tab to scroll/select text\n"
                "  Ctrl+Shift+C (or Shift+click) to copy from terminal"
            ),
        }))

    def _make_status(self) -> str:
        debug_state = self.debug_panel.get_status_text()
        cost_str = f"${self.total_cost:.4f}" if self.total_cost else "$0.0000"
        parts = [
            f"Turns: {self.turn_count}",
            f"Cost: {cost_str}",
            f"Debug: {debug_state}",
        ]
        if self.session_id:
            parts.append(f"Session: {self.session_id[:12]}...")
        return "  │  ".join(parts)

    def _update_status(self) -> None:
        status = self.query_one("#status-bar", Static)
        status.update(self._make_status())

    def _write_to_console(self, *renderables: Any) -> None:
        """Write one or more renderables to the conversation RichLog."""
        console = self.query_one("#conversation", RichLog)
        for r in renderables:
            if r is not None:
                console.write(r)
        console.scroll_end(animate=False)

    # ── Focus ──────────────────────────────────────────────────────────

    def action_focus_input(self) -> None:
        """Focus the input field (Escape key)."""
        self.query_one("#input", Input).focus()

    # ── Input handling ─────────────────────────────────────────────────

    def on_input_changed(self, event: Input.Changed) -> None:
        """Show available commands when user types /."""
        text = event.value.strip()
        if text.startswith("/") and " " not in text:
            # Show matching commands
            matching = [f"{cmd} — {desc}" for cmd, desc in COMMANDS.items() if cmd.startswith(text)]
            if matching:
                self._write_to_console(format_separator("Available commands"))
                for m in matching:
                    self._write_to_console(format_system_message("command", {"info": m}))

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input submission."""
        text = event.value.strip()
        event.input.value = ""

        if not text:
            return

        # Check for slash commands
        if text.startswith("/"):
            self._handle_command(text)
            return

        # Send to agent
        await self._send_to_agent(text)

    def _handle_command(self, text: str) -> None:
        """Handle slash commands."""
        parts = text.split(maxsplit=1)
        cmd = parts[0].lower()

        if cmd == "/debug":
            new_state = self.debug_panel.toggle()
            state_str = "ON" if new_state else "OFF"
            self._write_to_console(
                format_separator(f"Debug mode: {state_str}")
            )
            self._update_status()

        elif cmd == "/clear":
            self.action_clear_conversation()

        elif cmd == "/quit" or cmd == "/exit":
            self.exit()

        elif cmd == "/help":
            self._write_to_console(format_separator("Available commands"))
            for cmd_name, desc in COMMANDS.items():
                self._write_to_console(format_system_message("command", {"info": f"{cmd_name} — {desc}"}))

        else:
            self._write_to_console(
                format_error(f"Unknown command: {cmd}. Type /help for available commands.")
            )

    def action_clear_conversation(self) -> None:
        """Clear the conversation display."""
        console = self.query_one("#conversation", RichLog)
        console.clear()
        self.turn_count = 0
        self.total_cost = 0.0
        self.session_id = None
        self._update_status()
        self._write_to_console(format_separator("Conversation cleared"))

    def action_toggle_debug(self) -> None:
        """Toggle debug mode via keybinding."""
        new_state = self.debug_panel.toggle()
        state_str = "ON" if new_state else "OFF"
        self._write_to_console(format_separator(f"Debug mode: {state_str}"))
        self._update_status()

    # ── Agent interaction ──────────────────────────────────────────────

    async def _send_to_agent(self, prompt: str) -> None:
        """Send a prompt to the Claude Agent SDK and display the response."""
        if self.is_streaming:
            self._write_to_console(format_error("Already processing a request. Please wait..."))
            return

        self.is_streaming = True
        self._conversation_turn += 1
        self.turn_count += 1

        # Show user input
        self._write_to_console(format_separator(f"Turn {self._conversation_turn}"))
        self._write_to_console(format_user_input(prompt))

        # Show debug: about to send
        debug_msg = self.debug_panel.log_custom(
            f"Sending prompt ({len(prompt)} chars) to Claude Agent SDK..."
        )
        if debug_msg:
            self._write_to_console(debug_msg)

        # Run the SDK call in a worker
        self.run_worker(
            self._run_sdk_query(prompt),
            thread=True,
            exclusive=True,
            group="agent",
        )

    async def _run_sdk_query(self, prompt: str) -> None:
        """Run the Claude Agent SDK query in a background thread."""
        worker = get_current_worker()
        if worker.is_cancelled:
            return

        try:
            # Import SDK here to allow the TUI module to be imported
            # even if claude-agent-sdk is not installed
            from claude_agent_sdk import (
                query,
                ClaudeAgentOptions,
                AssistantMessage,
                UserMessage,
                TextBlock,
                ToolUseBlock,
                ToolResultBlock,
                ThinkingBlock,
                HookEventMessage,
                ResultMessage,
                SystemMessage,
            )

            options = self._build_options()

            async for msg in query(prompt=prompt, options=options):
                if worker.is_cancelled:
                    break

                # Debug logging
                debug_line = self.debug_panel.log_message(msg)
                raw_line = self.debug_panel.log_raw(msg)

                # Format and display based on message type
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            self.call_from_thread(
                                self._write_to_console,
                                format_assistant_text(block.text),
                                debug_line,
                            )
                        elif isinstance(block, ToolUseBlock):
                            self.call_from_thread(
                                self._write_to_console,
                                format_tool_use(block.name, block.input),
                                debug_line,
                            )
                        elif isinstance(block, ThinkingBlock):
                            self.call_from_thread(
                                self._write_to_console,
                                format_thinking(block.thinking),
                                debug_line,
                            )
                        elif isinstance(block, ToolResultBlock):
                            content = getattr(block, "content", None) or getattr(block, "output", "")
                            self.call_from_thread(
                                self._write_to_console,
                                format_tool_result(content),
                                debug_line,
                            )
                        else:
                            # Unknown block type — show full details
                            self.call_from_thread(
                                self._write_to_console,
                                format_full_message(f"block:{type(block).__name__}", block),
                                debug_line,
                            )

                elif isinstance(msg, ResultMessage):
                    self.total_cost = msg.total_cost_usd or 0.0
                    result_session = getattr(msg, "session_id", None)
                    if result_session:
                        self.session_id = result_session
                    self.call_from_thread(
                        self._write_to_console,
                        format_full_message("ResultMessage", msg),
                        debug_line,
                        raw_line,
                    )

                elif isinstance(msg, UserMessage):
                    self.call_from_thread(
                        self._write_to_console,
                        format_full_message("UserMessage", msg),
                        debug_line,
                    )

                elif isinstance(msg, HookEventMessage):
                    self.call_from_thread(
                        self._write_to_console,
                        format_full_message("HookEventMessage", msg),
                        debug_line,
                    )

                elif isinstance(msg, SystemMessage):
                    if hasattr(msg, "subtype") and msg.subtype == "init":
                        if hasattr(msg, "data") and isinstance(msg.data, dict):
                            self.session_id = msg.data.get("session_id")
                    self.call_from_thread(
                        self._write_to_console,
                        format_full_message("SystemMessage", msg),
                        debug_line,
                    )

                else:
                    # Unknown message type — show full details
                    self.call_from_thread(
                        self._write_to_console,
                        format_full_message(type(msg).__name__, msg),
                        debug_line,
                        raw_line,
                    )

        except Exception as e:
            self.call_from_thread(
                self._write_to_console,
                format_error(f"{type(e).__name__}: {e}"),
            )
        finally:
            self.call_from_thread(self._on_stream_complete)

    def _on_stream_complete(self) -> None:
        """Called when the SDK stream finishes."""
        self.is_streaming = False
        self._update_status()

    def _build_options(self) -> Any:
        """Build ClaudeAgentOptions from instance configuration."""
        from claude_agent_sdk import ClaudeAgentOptions

        kwargs: dict[str, Any] = {}
        if self.session_id:
            kwargs["resume"] = self.session_id
        if self.allowed_tools:
            kwargs["allowed_tools"] = self.allowed_tools
        if self.permission_mode:
            kwargs["permission_mode"] = self.permission_mode
        if self.max_turns:
            kwargs["max_turns"] = self.max_turns
        if self.max_budget_usd:
            kwargs["max_budget_usd"] = self.max_budget_usd
        return ClaudeAgentOptions(**kwargs)


# ── Standalone runner ──────────────────────────────────────────────────

if __name__ == "__main__":
    app = AgentTuiApp(
        allowed_tools=["Read", "Glob", "Grep"],
        permission_mode="acceptEdits",
    )
    app.run()
