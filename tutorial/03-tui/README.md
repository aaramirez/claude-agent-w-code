# Part 3: TUI Interactive Examples

Interactive terminal interface for the Claude Agent SDK. Everything the model sends or receives is displayed on screen with colors, making the agentic loop visible and didactic.

## What This Is

A [Textual](https://github.com/Textualize/textual)-based TUI that wraps the Claude Agent SDK into a beautiful, color-coded terminal experience:

- **User types prompts** in an input field
- **All model interactions** displayed with distinct colors
- **Debug mode ON by default** — see raw SDK messages
- **Slash commands** for controlling the TUI

## Setup

```bash
cd tutorial/03-tui
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-xxxxx   # macOS/Linux
# $env:ANTHROPIC_API_KEY = "sk-ant-xxxxx"  # Windows PowerShell
```

## Running Examples

```bash
# Basic interactive agent with file tools
python examples/01-basic-agent.py

# Visualize the agentic loop step-by-step
python examples/02-agentic-loop-visual.py

# Custom tools (calculator, weather, DB)
python examples/03-custom-tools-interactive.py

# KEY: AI models have no memory (demonstration)
python examples/04-no-memory.py

# Production patterns with safety limits
python examples/05-production-tui.py
```

## TUI Layout

```
┌─────────────────────────────────────────────────┐
│  Header: "Claude Agent TUI"    Debug: ON        │
├─────────────────────────────────────────────────┤
│                                                 │
│  Conversation Area (scrollable, color-coded)    │
│  ┌─────────────────────────────────────────┐    │
│  │ You: What files are here?               │    │
│  │                                         │    │
│  │ Claude: Here are the files...           │    │
│  │   → Tool: Glob({"pattern": "*.py"})     │    │
│  │   ← Result: ["main.py", "utils.py"]    │    │
│  │                                         │    │
│  │ [DEBUG] AssistantMessage → TextBlock    │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
├─────────────────────────────────────────────────┤
│  Turns: 3  │  Cost: $0.0045  │  Debug: ON      │
├─────────────────────────────────────────────────┤
│  > Type your prompt...                          │
└─────────────────────────────────────────────────┘
```

## Color Scheme

| Element | Color | Meaning |
|---------|-------|---------|
| `You:` | Cyan, bold | User input |
| `Claude:` | Green | Model text output |
| `→ Tool:` | Yellow | Tool call request |
| `← Result:` | Dim white | Tool execution result |
| `[System]` | Blue | System/init messages |
| `[ERROR]` | Red, bold | Errors |
| `── DONE ──` | Magenta | Loop completed |
| `[DEBUG]` | Gray, italic | Debug info (when debug=ON) |

## Commands

| Command | Action |
|---------|--------|
| `/debug` | Toggle debug mode ON/OFF |
| `/clear` | Clear conversation history |
| `/quit` | Exit the TUI |
| `/help` | Show available commands |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+D` | Toggle debug mode |
| `Ctrl+C` | Clear conversation |
| `Ctrl+Q` | Quit |

## Debug Mode

Debug mode is **ON by default**. It shows raw SDK message details:

```
[DEBUG] AssistantMessage blocks=[TextBlock, ToolUseBlock] stop=tool_use cost=$0.0012 turns=1 @ 14:32:05
[DEBUG] ResultMessage stop=end_turn turns=3 cost=$0.0045 @ 14:32:08
```

Toggle with `/debug` or `Ctrl+D`. When OFF, only formatted user-facing messages are shown.

## The No-Memory Example (04-no-memory.py)

This is the **key example** that demonstrates a fundamental truth about AI models:

**AI models have no persistent memory.**

The demo runs two scenarios:

### Part 1: Without Memory
```
Query 1: "My name is Carlos and I'm building a weather app"
Query 2: "What's my name and what am I building?"
→ Claude DOESN'T KNOW — each query is independent
```

### Part 2: With Memory (session resume)
```
Query 1: "My name is Carlos and I'm building a weather app"
Query 2 (resume session): "What's my name and what am I building?"
→ Claude REMEMBERS — session preserves context
```

The difference is clear: without explicit session management, every conversation starts from zero.

## Architecture

```
03-tui/
├── agent_tui.py          # Main Textual App (AgentTuiApp)
├── message_formatter.py  # SDK message → styled Rich Text
├── debug_panel.py        # Debug mode state and rendering
├── styles.tcss           # Textual CSS layout
├── requirements.txt      # Dependencies
├── README.md             # This file
└── examples/
    ├── 01-basic-agent.py
    ├── 02-agentic-loop-visual.py
    ├── 03-custom-tools-interactive.py
    ├── 04-no-memory.py
    └── 05-production-tui.py
```

## Extending

To create your own TUI example, subclass `AgentTuiApp`:

```python
from agent_tui import AgentTuiApp
from claude_agent_sdk import ClaudeAgentOptions

class MyApp(AgentTuiApp):
    def _build_options(self):
        return ClaudeAgentOptions(
            allowed_tools=["Read", "Glob"],
            permission_mode="acceptEdits",
            max_turns=5,
        )

app = MyApp()
app.run()
```

## Dependencies

- **textual** `>=0.40.0` — TUI framework
- **rich** `>=13.0.0` — Rich text rendering (Textual dependency)
- **claude-agent-sdk** — The agent SDK
