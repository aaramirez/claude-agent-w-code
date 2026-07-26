# TUI Interactive Agent + No-Memory Example

## Objective

Create a Textual-based TUI that wraps the Claude Agent SDK examples into an interactive terminal interface where users type prompts and see all model interactions beautifully formatted with colors, plus a dedicated example demonstrating that AI models have no persistent memory.

## Requirements

1. Interactive TUI where user types prompts and sees formatted model output — priority: high
2. Debug mode ON by default, toggled with `/debug` command — priority: high
3. All SDK messages displayed: user input, model text, tool calls, tool results, system messages — priority: high
4. Color-coded output for different message types — priority: high
5. No-memory example showing AI lacks conversation memory — priority: high
6. New directory `tutorial/03-tui/` separate from existing examples — priority: high
7. Works with Python 3.10+, depends on `textual` and `claude-agent-sdk` — priority: high
8. Slash commands: `/debug`, `/clear`, `/quit`, `/help` — priority: medium
9. Status bar showing turn count, cost, session state — priority: medium
10. README with setup instructions and usage guide — priority: medium

## Architecture

### Directory Structure

```
tutorial/03-tui/
├── README.md                    # Setup, usage, commands reference
├── requirements.txt             # textual, claude-agent-sdk
├── agent_tui.py                 # Main TUI application (Textual App)
├── message_formatter.py         # Formats SDK messages into styled Textual objects
├── debug_panel.py               # Debug mode rendering (raw message repr)
├── examples/
│   ├── 01-basic-agent.py        # Interactive agent with tools (default)
│   ├── 02-agentic-loop-visual.py # Visualizes the agentic loop step-by-step
│   ├── 03-custom-tools-interactive.py # User defines tools, agent uses them
│   ├── 04-no-memory.py          # Demonstrates AI has no memory (key example)
│   └── 05-production-tui.py     # Production patterns with TUI (tracing, limits)
└── styles.tcss                  # Textual CSS for layout and theming
```

### Core Components

#### `agent_tui.py` — Main Application

```python
class AgentTuiApp(App):
    """Interactive TUI for Claude Agent SDK examples."""
    
    # State
    debug_mode: bool = True          # ON by default
    conversation_history: list       # Messages for context
    session_id: str | None = None
    turn_count: int = 0
    total_cost: float = 0.0
    is_streaming: bool = False
    
    # Compose: Header → Conversation (RichLog) → Status Bar → Input
    # BINDINGS: ctrl+q=quit, ctrl+c=clear
    # Commands: /debug, /clear, /quit, /help
```

**Layout (compose):**
```
┌─────────────────────────────────────────────────┐
│  Header: "Claude Agent TUI"    Debug: ON  ⚡    │
├─────────────────────────────────────────────────┤
│                                                 │
│  Conversation Area (RichLog, scrollable)        │
│  ┌─────────────────────────────────────────┐    │
│  │ You: What files are here?               │    │
│  │                                         │    │
│  │ Claude: Here are the files...           │    │
│  │   → Tool: Glob({"pattern": "*.py"})     │    │
│  │   ← Result: ["main.py", "utils.py"]    │    │
│  │                                         │    │
│  │ [DEBUG] AssistantMessage → TextBlock    │    │
│  │ [DEBUG] cost: $0.0012 | turns: 1       │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
├─────────────────────────────────────────────────┤
│  Turns: 3  │  Cost: $0.0045  │  Session: abc  │
├─────────────────────────────────────────────────┤
│  > Type your prompt...                          │
└─────────────────────────────────────────────────┘
```

**Key methods:**
- `on_input_submitted()` — parse input, check for `/commands`, else send to agent
- `action_toggle_debug()` — flip `debug_mode`, update header
- `send_to_agent(prompt)` — runs SDK `query()` in a Textual worker, streams messages back
- `format_and_display(msg)` — routes each message type to the formatter, writes to RichLog

#### `message_formatter.py` — Message Rendering

Formats each SDK message type into styled `Text` objects for the RichLog:

| Message Type | Display Style | Color |
|-------------|---------------|-------|
| User input | `You: {text}` | Cyan, bold |
| TextBlock | `Claude: {text}` | Green |
| ToolUseBlock | `→ Tool: {name}({args})` | Yellow |
| ToolResultBlock | `← Result: {truncated_content}` | Dim white |
| ResultMessage | `── DONE ── turns:N cost:$X reason:...` | Magenta |
| SystemMessage | `[System] {info}` | Blue |
| Error | `[ERROR] {message}` | Red, bold |
| Debug (raw) | `[DEBUG] {type}: {repr}` | Gray, italic |

**Debug mode behavior:**
- ON: All messages shown including `[DEBUG]` raw repr lines
- OFF: Only formatted user-facing messages (no debug lines)

#### `debug_panel.py` — Debug Rendering

Renders raw SDK message data for debugging:
- Full message type name
- Content block types and counts
- Token usage if available
- Stop reason and terminal reason
- Timestamp

### No-Memory Example (`04-no-memory.py`)

**Concept:** AI models are stateless — each API call is independent unless you explicitly pass conversation history.

**Demo flow:**

```
═══════════════════════════════════════════════
 PART 1: WITHOUT MEMORY (no session, no history)
═══════════════════════════════════════════════

Query 1: "My name is Carlos and I'm building a weather app"
→ Claude responds (acknowledges, discusses weather app)

Query 2: "What's my name and what am I building?"
→ Claude responds: "I don't have access to your name or previous 
   conversation. Each conversation starts fresh..."
   
❌ Claude doesn't remember! No memory across separate queries.

═══════════════════════════════════════════════
 PART 2: WITH MEMORY (using session resume)
═══════════════════════════════════════════════

Query 1: "My name is Carlos and I'm building a weather app"
→ Claude responds, session_id captured

Query 2 (resume=session_id): "What's my name and what am I building?"
→ Claude responds: "Your name is Carlos and you're building a 
   weather app..."
   
✅ Claude remembers! Session resume preserves context.
```

**Implementation:**
- Uses `ClaudeSDKClient` for Part 2 (session persistence)
- Uses standalone `query()` calls for Part 1 (no history)
- Side-by-side comparison in TUI with clear visual separation
- Color-coded: Part 1 in red/dim (no memory), Part 2 in green (memory works)

### TUI Examples (`01-basic-agent.py` through `05-production-tui.py`)

Each example is a standalone Textual app that:
1. Imports `AgentTuiApp` from `agent_tui.py`
2. Configures specific tools/options
3. Overrides the default prompt or adds custom behavior
4. Can be run standalone: `python examples/01-basic-agent.py`

**`01-basic-agent.py`** — Default interactive agent with Read, Glob, Grep tools. User types anything, agent responds with formatted output.

**`02-agentic-loop-visual.py`** — Step-by-step visualization of the agentic loop. Each iteration is numbered and color-coded. Shows `stop_reason` transitions.

**`03-custom-tools-interactive.py`** — Agent with calculator, weather, and DB tools. User can ask questions that trigger tool calls. Shows how tools work in the TUI.

**`04-no-memory.py`** — The memory demonstration example (described above).

**`05-production-tui.py`** — Production patterns: max_turns limit, cost tracking, error handling. Shows how the TUI displays limits being hit.

### `styles.tcss` — Textual CSS

```css
Screen {
    background: $surface;
}

#conversation {
    height: 1fr;
    border: solid $accent;
    padding: 1 2;
}

#input {
    dock: bottom;
    margin: 1 0;
}

#status-bar {
    dock: bottom;
    height: 1;
    background: $accent;
    color: $text;
}
```

## Library/Dependencies

| Library | Version | Purpose | Context7 |
|---------|---------|---------|----------|
| `textual` | ≥0.40.0 | TUI framework | `/textualize/textual` |
| `rich` | ≥13.0.0 | Rich text rendering (Textual dependency) | `/textualize/rich` |
| `claude-agent-sdk` | latest | Agent SDK (already used) | N/A |

**Textual API notes:**
- `App.compose()` returns `ComposeResult` with widgets
- `RichLog.write()` accepts `str | RenderableType` for styled output
- `@work(thread=True)` for background async SDK calls
- `App.call_from_thread()` for safe UI updates from worker threads
- `BINDINGS` list for keyboard shortcuts
- `.tcss` files for declarative styling

## File Changes

### New files (all under `tutorial/03-tui/`):
1. `README.md` — overview, setup, commands reference
2. `requirements.txt` — dependencies
3. `agent_tui.py` — main TUI application class
4. `message_formatter.py` — message type → styled text
5. `debug_panel.py` — debug mode rendering
6. `styles.tcss` — Textual CSS layout
7. `examples/01-basic-agent.py` — interactive agent
8. `examples/02-agentic-loop-visual.py` — loop visualization
9. `examples/03-custom-tools-interactive.py` — custom tools demo
10. `examples/04-no-memory.py` — no-memory demonstration
11. `examples/05-production-tui.py` — production patterns

### Modified files:
12. `tutorial/README.md` — add Part 3: TUI Interactive Examples link
13. `tutorial/examples/README.md` — add TUI examples section

## TDD Flow

1. **Write test for message_formatter.py** — verify each message type produces correct styled output
2. **Write test for debug_panel.py** — verify debug toggle shows/hides raw repr
3. **Implement message_formatter.py** — tests pass
4. **Implement debug_panel.py** — tests pass
5. **Write test for agent_tui.py** — verify input submission triggers agent call
6. **Implement agent_tui.py** — tests pass
7. **Write test for 04-no-memory.py** — verify Part 1 fails to remember, Part 2 remembers
8. **Implement 04-no-memory.py** — tests pass
9. **Implement remaining examples** — all pass
10. **Refactor** — clean up, ensure consistent style

## Verification

- [ ] `pip install -r requirements.txt` succeeds
- [ ] `python agent_tui.py` launches the TUI
- [ ] User can type prompts and see formatted responses
- [ ] `/debug` command toggles debug mode on/off
- [ ] Debug mode shows raw message repr when ON
- [ ] Debug mode hides debug lines when OFF
- [ ] All 5 examples run standalone
- [ ] `04-no-memory.py` clearly shows Part 1 (no memory) vs Part 2 (memory)
- [ ] Colors are correct for each message type
- [ ] Status bar updates with turn count and cost
- [ ] `/clear` resets the conversation
- [ ] `/help` shows available commands
- [ ] README explains setup and usage
