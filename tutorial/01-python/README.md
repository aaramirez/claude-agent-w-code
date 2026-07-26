# Python Track

## Setup

### 1. Install the SDK

```bash
pip install claude-agent-sdk
```

Or with [uv](https://docs.astral.sh/uv/) (recommended):

```bash
uv init
uv add claude-agent-sdk
```

### 2. Set Your API Key

```bash
# macOS/Linux
export ANTHROPIC_API_KEY=sk-ant-xxxxx

# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-xxxxx"
```

Get a key at [console.anthropic.com](https://console.anthropic.com).

### 3. Run an Example

```bash
cd tutorial/01-python
python 01-hello-agent.py
```

Or with uv:

```bash
uv run 01-hello-agent.py
```

## What You'll Learn

Each file builds on the previous one. Start with `01-hello-agent.py` and work your way through.

The files with explanations are in `../00-how-llms-enable-agents/` — read those first if you want to understand the "why" before the "how".

### Deep Dives

| Document | Description |
|----------|-------------|
| [RESPONSE_ANATOMY.md](RESPONSE_ANATOMY.md) | Field-by-field dissection of every message in a real run |
| [MESSAGE_FLOWS.md](MESSAGE_FLOWS.md) | All message types, flow diagrams, and state transitions |

## Files

| # | File | Concept |
|---|------|---------|
| 1 | `01-hello-agent.py` | `query()`, streaming messages, basic setup |
| 2 | `02-agentic-loop.py` | `AssistantMessage`, `ToolUseBlock`, `stop_reason` |
| 3 | `03-built-in-tools.py` | `Read`, `Bash`, `Glob`, `Grep` |
| 4 | `04-custom-tools.py` | `@tool`, `create_sdk_mcp_server()` |
| 5 | `05-bidirectional-streaming.py` | `ClaudeSDKClient`, interactive sessions |
| 6 | `06-hooks.py` | `PreToolUse`, `PostToolUse` |
| 7 | `07-permissions.py` | `can_use_tool`, `PermissionResultDeny` |
| 8 | `08-subagents.py` | `AgentDefinition`, worker delegation |
| 9 | `09-sessions.py` | `session_id`, `resume` |
| 10 | `10-production.py` | Tracing, cost control, `max_turns` |
| 11 | `11-mcp-integration.py` | External MCP servers |
