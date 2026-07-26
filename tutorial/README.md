# Claude Agent SDK Tutorial

Learn to build AI agents from zero to production using the Claude Agent SDK — in Python or Node.js.

## What You'll Learn

This tutorial has two tracks (pick your language) plus a conceptual foundation that explains **how the model actually works** so you understand *why* agents work, not just how to code them.

### Part 0: How LLMs Enable Agents (read first)

Before writing any code, understand the fundamentals:

1. [How Language Models Work](00-how-llms-enable-agents/01-how-language-models-work.md) — token prediction, context windows
2. [Tool Calls Are Just Computer Programs](00-how-llms-enable-agents/02-tool-use-at-the-model-level.md) — what happens when the model says "call this tool"
3. [The Agentic Loop](00-how-llms-enable-agents/03-the-agentic-loop-explained.md) — `stop_reason`, `tool_use`, `end_turn`
4. [The Message Protocol](00-how-llms-enable-agents/04-message-protocol.md) — content blocks, message types, data flow

### Part 1: Python Track

| # | File | What You Learn |
|---|------|----------------|
| 1 | [01-hello-agent.py](01-python/01-hello-agent.py) | Install SDK, set API key, first agent |
| 2 | [02-agentic-loop.py](01-python/02-agentic-loop.py) | Observe the loop: stop_reason, content blocks |
| 3 | [03-built-in-tools.py](01-python/03-built-in-tools.py) | Read, Bash, Glob, Grep in action |
| 4 | [04-custom-tools.py](01-python/04-custom-tools.py) | Build your own tools with `@tool` |
| 5 | [05-bidirectional-streaming.py](01-python/05-bidirectional-streaming.py) | `ClaudeSDKClient` interactive sessions |
| 6 | [06-hooks.py](01-python/06-hooks.py) | Lifecycle hooks: PreToolUse, PostToolUse |
| 7 | [07-permissions.py](01-python/07-permissions.py) | Fine-grained tool permissions |
| 8 | [08-subagents.py](01-python/08-subagents.py) | Spawn specialized worker agents |
| 9 | [09-sessions.py](01-python/09-sessions.py) | Resume context across conversations |
| 10 | [10-production.py](01-python/10-production.py) | Tracing, cost control, error handling |
| 11 | [11-mcp-integration.py](01-python/11-mcp-integration.py) | Connect external MCP servers |

### Part 3: TUI Interactive Examples

Interactive terminal interface with colors — everything the model sends/receives is displayed on screen.

| # | File | What You Learn |
|---|------|----------------|
| 1 | [01-basic-agent.py](03-tui/examples/01-basic-agent.py) | Interactive agent with file tools |
| 2 | [02-agentic-loop-visual.py](03-tui/examples/02-agentic-loop-visual.py) | Step-by-step loop visualization |
| 3 | [03-custom-tools-interactive.py](03-tui/examples/03-custom-tools-interactive.py) | Custom tools in the TUI |
| 4 | [04-no-memory.py](03-tui/examples/04-no-memory.py) | **AI models have no memory** (key demo) |
| 5 | [05-production-tui.py](03-tui/examples/05-production-tui.py) | Production patterns with TUI |

See the [TUI README](03-tui/README.md) for setup, commands, and architecture.

### Part 2: Node.js/TypeScript Track

| # | File | What You Learn |
|---|------|----------------|
| 1 | [01-hello-agent.ts](02-nodejs/01-hello-agent.ts) | Install SDK, set API key, first agent |
| 2 | [02-agentic-loop.ts](02-nodejs/02-agentic-loop.ts) | Observe the loop: stop_reason, content blocks |
| 3 | [03-built-in-tools.ts](02-nodejs/03-built-in-tools.ts) | Read, Bash, Glob, Grep in action |
| 4 | [04-custom-tools.ts](02-nodejs/04-custom-tools.ts) | Build your own tools with `tool()` |
| 5 | [05-bidirectional-streaming.ts](02-nodejs/05-bidirectional-streaming.ts) | `ClaudeSDKClient` interactive sessions |
| 6 | [06-hooks.ts](02-nodejs/06-hooks.ts) | Lifecycle hooks: PreToolUse, PostToolUse |
| 7 | [07-permissions.ts](02-nodejs/07-permissions.ts) | Fine-grained tool permissions |
| 8 | [08-subagents.ts](02-nodejs/08-subagents.ts) | Spawn specialized worker agents |
| 9 | [09-sessions.ts](02-nodejs/09-sessions.ts) | Resume context across conversations |
| 10 | [10-production.ts](02-nodejs/10-production.ts) | Tracing, cost control, error handling |
| 11 | [11-mcp-integration.ts](02-nodejs/11-mcp-integration.ts) | Connect external MCP servers |

## Prerequisites

- **Python 3.10+** or **Node.js 18+**
- An Anthropic API key ([get one here](https://console.anthropic.com))
- `ANTHROPIC_API_KEY` set in your environment

```bash
# macOS/Linux
export ANTHROPIC_API_KEY=sk-ant-xxxxx

# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-xxxxx"
```

## Quick Start

**Python:**
```bash
pip install claude-agent-sdk
cd tutorial/01-python
python 01-hello-agent.py
```

**Node.js:**
```bash
npm init -y && npm pkg set type=module
npm install @anthropic-ai/claude-agent-sdk
npm install --save-dev tsx
cd tutorial/02-nodejs
npx tsx 01-hello-agent.ts
```

## How to Use This Tutorial

1. **Read Part 0 first** — the conceptual foundation explains WHY agents work
2. **Pick your language track** — Python or Node.js
3. **Run each example** — modify the prompts, break things, experiment
4. **Read the explanation blocks** — each example has detailed commentary
5. **Progress linearly** — later examples build on earlier concepts

## Key Concept: The Agentic Loop

The core of every agent is a simple loop:

```
You send prompt
    ↓
Model responds (text OR tool_use)
    ↓
If tool_use → execute the tool (it's just a program) → append result → loop back
If end_turn → done, return response
```

The model decides WHAT to do. Your tools do the actual work. The loop connects them.

Tools can be **anything a computer can execute**: read files, call APIs, query databases, run shell commands, automate browsers, control hardware, send emails — locally or across the internet.
