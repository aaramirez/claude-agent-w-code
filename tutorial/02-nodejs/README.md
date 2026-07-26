# Node.js/TypeScript Track

## Setup

### 1. Install the SDK

```bash
npm init -y
npm pkg set type=module
npm install @anthropic-ai/claude-agent-sdk
npm install --save-dev tsx
```

Setting `"type": "module"` in `package.json` enables top-level `await`.

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
cd tutorial/02-nodejs
npx tsx 01-hello-agent.ts
```

## What You'll Learn

Each file builds on the previous one. Start with `01-hello-agent.ts` and work your way through.

The conceptual foundation is in `../00-how-llms-enable-agents/` — read those first if you want to understand the "why" before the "how".

### Deep Dives

| Document | Description |
|----------|-------------|
| [MESSAGE_FLOWS.md](MESSAGE_FLOWS.md) | All message types, flow diagrams, and state transitions |

## Files

| # | File | Concept |
|---|------|---------|
| 1 | `01-hello-agent.ts` | `query()`, streaming messages, basic setup |
| 2 | `02-agentic-loop.ts` | AssistantMessage, ToolUseBlock, stop_reason |
| 3 | `03-built-in-tools.ts` | Read, Bash, Glob, Grep |
| 4 | `04-custom-tools.ts` | `tool()`, `createMcpServer()` |
| 5 | `05-bidirectional-streaming.ts` | `ClaudeSDKClient`, interactive sessions |
| 6 | `06-hooks.ts` | PreToolUse, PostToolUse |
| 7 | `07-permissions.ts` | `canUseTool`, permission deny |
| 8 | `08-subagents.ts` | AgentDefinition, delegation |
| 9 | `09-sessions.ts` | sessionId, resume |
| 10 | `10-production.ts` | Tracing, cost control, maxTurns |
| 11 | `11-mcp-integration.ts` | External MCP servers |
