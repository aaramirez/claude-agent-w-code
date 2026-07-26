"""
Debug Panel — Controls what gets displayed based on debug mode state.

When debug_mode is True (default):
  - All formatted messages are shown
  - Raw [DEBUG] lines with message type, block counts, timing are shown
  - [RAW] repr lines available for deep inspection

When debug_mode is False:
  - Only formatted user-facing messages (user input, model text, tool calls/results)
  - No [DEBUG] or [RAW] lines
  - Cleaner, more readable output
"""

from __future__ import annotations

from typing import Any

from rich.text import Text

from message_formatter import (
    format_debug_message,
    format_debug_raw,
    STYLE_DEBUG,
)


class DebugPanel:
    """Manages debug output based on the current debug mode state."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._message_count = 0

    def toggle(self) -> bool:
        """Toggle debug mode. Returns new state."""
        self.enabled = not self.enabled
        return self.enabled

    def log_message(self, msg: Any) -> Text | None:
        """
        Log a message in debug mode.
        Returns formatted debug Text if debug is on, None otherwise.
        """
        if not self.enabled:
            return None

        self._message_count += 1
        return format_debug_message(msg)

    def log_raw(self, msg: Any) -> Text | None:
        """
        Log raw repr of a message in debug mode.
        Returns formatted raw Text if debug is on, None otherwise.
        """
        if not self.enabled:
            return None

        return format_debug_raw(msg)

    def log_custom(self, text: str, style: str = "") -> Text | None:
        """
        Log a custom debug message.
        Returns formatted Text if debug is on, None otherwise.
        """
        if not self.enabled:
            return None

        result = Text()
        result.append(f"  [DEBUG] ", style=STYLE_DEBUG)
        if style:
            result.append(f"{text}\n", style=style)
        else:
            result.append(f"{text}\n", style=STYLE_DEBUG)
        return result

    def get_status_text(self) -> str:
        """Return debug mode status for display in header/status bar."""
        return "ON" if self.enabled else "OFF"

    @property
    def message_count(self) -> int:
        return self._message_count
