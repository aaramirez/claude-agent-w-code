# Runnable Examples Index

All examples in this directory can be run directly. Pick your language.

## Python

Requires: Python 3.10+, `pip install claude-agent-sdk`

```bash
cd tutorial/01-python

# Start simple
python 01-hello-agent.py

# See the agentic loop in action
python 02-agentic-loop.py

# Use built-in tools
python 03-built-in-tools.py

# Create custom tools
python 04-custom-tools.py

# Interactive sessions
python 05-bidirectional-streaming.py

# Add lifecycle hooks
python 06-hooks.py

# Fine-grained permissions
python 07-permissions.py

# Spawn subagents
python 08-subagents.py

# Resume sessions
python 09-sessions.py

# Production patterns
python 10-production.py

# Connect external MCP servers
python 11-mcp-integration.py
```

## Node.js/TypeScript

Requires: Node.js 18+, `npm install @anthropic-ai/claude-agent-sdk`, `npm install --save-dev tsx`

```bash
cd tutorial/02-nodejs

# Start simple
npx tsx 01-hello-agent.ts

# See the agentic loop in action
npx tsx 02-agentic-loop.ts

# Use built-in tools
npx tsx 03-built-in-tools.ts

# Create custom tools
npx tsx 04-custom-tools.ts

# Interactive sessions
npx tsx 05-bidirectional-streaming.ts

# Add lifecycle hooks
npx tsx 06-hooks.ts

# Fine-grained permissions
npx tsx 07-permissions.ts

# Spawn subagents
npx tsx 08-subagents.ts

# Resume sessions
npx tsx 09-sessions.ts

# Production patterns
npx tsx 10-production.ts

# Connect external MCP servers
npx tsx 11-mcp-integration.ts
```

## TUI Interactive

Requires: Python 3.10+, `pip install -r tutorial/03-tui/requirements.txt`

```bash
cd tutorial/03-tui

# Basic interactive agent
python examples/01-basic-agent.py

# Visualize the agentic loop step-by-step
python examples/02-agentic-loop-visual.py

# Custom tools (calculator, weather, DB)
python examples/03-custom-tools-interactive.py

# KEY: AI models have no memory
python examples/04-no-memory.py

# Production patterns with safety limits
python examples/05-production-tui.py
```

The TUI is a [Textual](https://github.com/Textualize/textual)-based terminal app with debug mode ON by default.

## Prerequisites

Set your API key before running any example:

```bash
# macOS/Linux
export ANTHROPIC_API_KEY=sk-ant-xxxxx

# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-xxxxx"
```

## Example Progression

| # | Concept | What It Shows |
|---|---------|---------------|
| 01 | Hello Agent | Minimal agent, no tools, just text |
| 02 | Agentic Loop | Observe stop_reason, content blocks, tool calls |
| 03 | Built-in Tools | Read, Bash, Glob, Grep in combination |
| 04 | Custom Tools | Build your own tools — any function, local or remote |
| 05 | Streaming | Interactive multi-turn sessions |
| 06 | Hooks | Intercept tool calls for logging/validation |
| 07 | Permissions | Fine-grained control over tool execution |
| 08 | Subagents | Specialized workers with isolated contexts |
| 09 | Sessions | Save and resume conversation context |
| 10 | Production | Tracing, cost control, error handling |
| 11 | MCP | Connect external tool servers (local or remote) |
