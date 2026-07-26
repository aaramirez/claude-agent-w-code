"""
Message Formatter — Converts Claude Agent SDK messages into styled Rich Text objects.

Each message type gets a distinct color and format so the TUI output is
visually clear and didactic. Debug mode adds raw message repr lines.

Color scheme:
  User input    → Cyan, bold
  Model text    → Green
  Tool calls    → Yellow
  Tool results  → Dim white
  System msgs   → Blue
  Errors        → Red, bold
  Result msgs   → Magenta
  Debug (raw)   → Gray, italic
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from rich.text import Text
from rich.panel import Panel
from rich.syntax import Syntax


# ── Color constants (Rich style strings) ───────────────────────────────

STYLE_USER = "bold cyan"
STYLE_TEXT = "green"
STYLE_TOOL_USE = "yellow"
STYLE_TOOL_RESULT = "dim white"
STYLE_SYSTEM = "blue"
STYLE_ERROR = "bold red"
STYLE_RESULT = "magenta"
STYLE_DEBUG = "italic gray50"
STYLE_HEADER = "bold white on blue"


# ── Public API ─────────────────────────────────────────────────────────

def format_user_input(text: str) -> Text:
    """Format user input for display."""
    return Text(f"  You: {text}", style=STYLE_USER)


def format_assistant_text(text: str) -> Text:
    """Format model text output."""
    result = Text()
    result.append("  Claude: ", style=STYLE_TEXT)
    # Split into lines to avoid single massive line
    lines = text.split("\n")
    for i, line in enumerate(lines):
        result.append(line, style=STYLE_TEXT)
        if i < len(lines) - 1:
            result.append("\n", style=STYLE_TEXT)
    return result


def format_tool_use(name: str, arguments: dict[str, Any] | str) -> Text:
    """Format a tool call request from the model."""
    if isinstance(arguments, dict):
        args_str = json.dumps(arguments, indent=2, default=str)
    else:
        args_str = str(arguments) if arguments else "(no arguments)"

    result = Text()
    result.append("    -> Tool: ", style=STYLE_TOOL_USE)
    result.append(f"{name}\n", style="bold yellow")
    # Indent args on separate lines so wrapping works cleanly
    for line in args_str.split("\n"):
        result.append(f"      {line}\n", style=STYLE_TOOL_USE)
    return result


def format_thinking(thinking_text: str) -> Text:
    """Format thinking/reasoning blocks from the model."""
    result = Text()
    result.append("    [thinking] ", style="italic gray50")
    if thinking_text:
        for line in thinking_text.split("\n"):
            result.append(f"      {line}\n", style="italic gray50")
    else:
        result.append("(empty)\n", style="italic gray50")
    return result


def format_tool_result(content: str | list, max_length: int = 0) -> Text:
    """Format a tool execution result."""
    if isinstance(content, list):
        # Extract text from content blocks
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
        content_str = " ".join(parts)
    else:
        content_str = str(content)

    # Truncate long results only if max_length > 0
    if max_length > 0 and len(content_str) > max_length:
        content_str = content_str[:max_length] + f"... ({len(content_str) - max_length} chars truncated)"

    result = Text()
    result.append("    <- Result:\n", style=STYLE_TOOL_RESULT)
    # Split content into indented lines for readability
    for line in content_str.split("\n"):
        result.append(f"      {line}\n", style=STYLE_TOOL_RESULT)
    return result


def format_result_message(
    stop_reason: str | None = None,
    terminal_reason: str | None = None,
    num_turns: int | None = None,
    cost_usd: float | None = None,
    session_id: str | None = None,
) -> Text:
    """Format the final ResultMessage (end of agentic loop)."""
    result = Text()
    result.append("\n  \u2500\u2500 DONE ", style=STYLE_RESULT)
    result.append("\u2500" * 40 + "\n", style=STYLE_RESULT)

    if stop_reason:
        result.append(f"    Stop reason:    {stop_reason}\n", style=STYLE_RESULT)
    if terminal_reason:
        result.append(f"    Terminal:       {terminal_reason}\n", style=STYLE_RESULT)
    if num_turns is not None:
        result.append(f"    Turns:          {num_turns}\n", style=STYLE_RESULT)
    if cost_usd is not None:
        result.append(f"    Cost:           ${cost_usd:.4f}\n", style=STYLE_RESULT)
    if session_id:
        result.append(f"    Session:        {session_id}\n", style=STYLE_RESULT)

    result.append("\n", style=STYLE_RESULT)
    return result


def format_system_message(subtype: str, data: dict | None = None) -> Text:
    """Format a system/init message."""
    result = Text()
    result.append(f"  [System] ", style=STYLE_SYSTEM)
    result.append(f"{subtype}", style="bold blue")
    if data:
        if "session_id" in data:
            result.append(f" session={data['session_id']}", style=STYLE_SYSTEM)
    result.append("\n", style=STYLE_SYSTEM)
    return result


def format_error(message: str) -> Text:
    """Format an error message."""
    return Text(f"  [ERROR] {message}\n", style=STYLE_ERROR)


def format_full_message(msg_type: str, msg: Any) -> Text:
    """Display ALL fields of any SDK message type — formatted JSON for nested structures."""
    result = Text()
    result.append(f"  [{msg_type}]\n", style=STYLE_SYSTEM)

    # Get all dataclass fields or attributes
    fields = {}
    if hasattr(msg, "__dataclass_fields__"):
        for name in msg.__dataclass_fields__:
            try:
                fields[name] = getattr(msg, name)
            except Exception:
                fields[name] = "<error>"
    elif hasattr(msg, "__dict__"):
        fields = vars(msg)
    else:
        for attr in dir(msg):
            if not attr.startswith("_"):
                try:
                    val = getattr(msg, attr)
                    if not callable(val):
                        fields[attr] = val
                except Exception:
                    pass

    # Render each field
    for name, value in fields.items():
        result.append(f"    {name}: ", style="bold")
        _append_value(result, value, indent=6)
        result.append("\n")

    return result


def _append_value(text: Text, value: Any, indent: int = 0) -> None:
    """Append a value to a Rich Text object with proper JSON-style formatting."""
    pad = " " * indent
    if value is None:
        text.append("None", style="dim")
    elif isinstance(value, str):
        text.append(f'"{value}"', style="dim green")
    elif isinstance(value, (int, float)):
        text.append(str(value), style="yellow")
    elif isinstance(value, bool):
        text.append(str(value), style="yellow")
    elif hasattr(value, "__dataclass_fields__"):
        # Convert dataclass to dict for pretty printing
        fields = {}
        for name in value.__dataclass_fields__:
            try:
                fields[name] = getattr(value, name)
            except Exception:
                fields[name] = "<error>"
        _append_value(text, fields, indent=indent)
    elif hasattr(value, "__dict__") and not isinstance(value, str):
        # Convert object with __dict__ to dict for pretty printing
        _append_value(text, vars(value), indent=indent)
    elif isinstance(value, dict):
        if not value:
            text.append("{}", style="dim")
            return
        text.append("{\n", style="bold")
        items = list(value.items())
        for i, (k, v) in enumerate(items):
            text.append(f"{pad}  ", style="dim")
            text.append(f'"{k}"', style="bold cyan")
            text.append(": ", style="dim")
            _append_value(text, v, indent=indent + 2)
            if i < len(items) - 1:
                text.append(",", style="dim")
            text.append("\n", style="dim")
        text.append(f"{pad}}}", style="bold")
    elif isinstance(value, (list, tuple)):
        if not value:
            text.append("[]", style="dim")
            return
        text.append("[\n", style="bold")
        for i, item in enumerate(value):
            text.append(f"{pad}  ", style="dim")
            _append_value(text, item, indent=indent + 2)
            if i < len(value) - 1:
                text.append(",", style="dim")
            text.append("\n", style="dim")
        text.append(f"{pad}]", style="bold")
    else:
        # For other objects, use repr
        text.append(repr(value), style="dim")


def format_separator(title: str = "") -> Text:
    """Format a visual separator line."""
    result = Text()
    if title:
        result.append(f"\n  -- {title} ", style="bold")
        result.append("-" * max(0, 50 - len(title)) + "\n\n", style="dim")
    else:
        result.append("\n  " + "-" * 55 + "\n\n", style="dim")
    return result


# ── Debug formatting ───────────────────────────────────────────────────

def format_debug_message(msg: Any) -> Text:
    """Format a raw SDK message for debug display."""
    result = Text()
    msg_type = type(msg).__name__

    result.append(f"  [DEBUG] ", style=STYLE_DEBUG)
    result.append(f"{msg_type}", style="bold italic gray50")

    # Extract useful debug info based on message type
    if hasattr(msg, "content") and msg.content:
        block_types = []
        for block in msg.content:
            block_type = type(block).__name__
            block_types.append(block_type)
        result.append(f" blocks={block_types}", style=STYLE_DEBUG)

    if hasattr(msg, "stop_reason") and msg.stop_reason:
        result.append(f" stop={msg.stop_reason}", style=STYLE_DEBUG)

    if hasattr(msg, "total_cost_usd") and msg.total_cost_usd:
        result.append(f" cost=${msg.total_cost_usd:.4f}", style=STYLE_DEBUG)

    if hasattr(msg, "num_turns") and msg.num_turns is not None:
        result.append(f" turns={msg.num_turns}", style=STYLE_DEBUG)

    if hasattr(msg, "subtype"):
        result.append(f" subtype={msg.subtype}", style=STYLE_DEBUG)

    if hasattr(msg, "data") and isinstance(msg.data, dict):
        if "session_id" in msg.data:
            result.append(f" session={msg.data['session_id']}", style=STYLE_DEBUG)

    result.append(f" @ {datetime.now().strftime('%H:%M:%S')}", style=STYLE_DEBUG)
    result.append("\n", style=STYLE_DEBUG)
    return result


def format_debug_raw(msg: Any) -> Text:
    """Format the full repr of a message for deep debug."""
    result = Text()
    result.append(f"  [RAW] ", style=STYLE_DEBUG)
    try:
        repr_str = repr(msg)
        if len(repr_str) > 300:
            repr_str = repr_str[:300] + "..."
        result.append(f"{repr_str}\n", style=STYLE_DEBUG)
    except Exception:
        result.append(f"<cannot repr {type(msg).__name__}>\n", style=STYLE_DEBUG)
    return result
