# Claude Agent SDK Tutorial — From Basics to Advanced

## Objective
Create a comprehensive, pedagogical tutorial teaching developers how to build AI agents using the Claude Agent SDK in both Python and Node.js, with deep explanations of how the underlying LLM enables agent programming — covering the agentic loop, tool use, stop reasons, and advanced patterns from zero to production.

## Requirements
1. Dual-language support: all examples in both Python and Node.js/TypeScript — priority: high
2. Deep model explanation sections: how LLMs work, why tool use is possible, what `stop_reason` means at the model level — priority: high
3. Progressive difficulty: basic → intermediate → advanced — priority: high
4. Working code examples for every concept taught — priority: high
5. Coverage of the agentic loop: `stop_reason`, `tool_use`, appending tool results, continuing to `end_turn` — priority: high
6. Custom tools with `@tool` decorator (Python) and tool definitions (TypeScript) — priority: high
7. Bidirectional streaming with `ClaudeSDKClient` — priority: high
8. Hooks and permissions — priority: medium
9. Subagents and sessions — priority: medium
10. MCP server integration — priority: medium
11. Error handling and production patterns — priority: medium

## Architecture — File Tree

```
tutorial/
├── README.md                                    # Overview, table of contents, how to use

├── 00-how-llms-enable-agents/
│   ├── 01-how-language-models-work.md           # What the model actually does
│   ├── 02-tool-use-at-the-model-level.md        # Why models can call tools
│   ├── 03-the-agentic-loop-explained.md         # stop_reason, tool_use, end_turn
│   └── 04-message-protocol.md                   # Content blocks, types, flow

├── 01-python/
│   ├── README.md                                # Python track overview + setup
│   ├── 01-hello-agent.py                        # Minimal agent with query()
│   ├── 02-agentic-loop.py                       # Observe the loop: stop_reason, content blocks
│   ├── 03-built-in-tools.py                     # Read, Bash, Glob, Grep in action
│   ├── 04-custom-tools.py                       # @tool + create_sdk_mcp_server()
│   ├── 05-bidirectional-streaming.py            # ClaudeSDKClient: connect, query, receive_response
│   ├── 06-hooks.py                              # PreToolUse, PostToolUse lifecycle
│   ├── 07-permissions.py                        # can_use_tool, PermissionResultDeny
│   ├── 08-subagents.py                          # AgentDefinition, delegation
│   ├── 09-sessions.py                           # session_id, resume, fork
│   ├── 10-production.py                         # Tracing, cost, error handling, max_turns
│   └── 11-mcp-integration.py                    # External MCP servers (Playwright, etc.)

├── 02-nodejs/
│   ├── README.md                                # Node.js track overview + setup
│   ├── 01-hello-agent.ts                        # Minimal agent with query()
│   ├── 02-agentic-loop.ts                       # Observe the loop: stop_reason, content blocks
│   ├── 03-built-in-tools.ts                     # Read, Bash, Glob, Grep in action
│   ├── 04-custom-tools.ts                       # tool() + createMcpServer()
│   ├── 05-bidirectional-streaming.ts            # ClaudeSDKClient: connect, query, receiveResponse
│   ├── 06-hooks.ts                              # PreToolUse, PostToolUse lifecycle
│   ├── 07-permissions.ts                        # canUseTool, permission deny
│   ├── 08-subagents.ts                          # AgentDefinition, delegation
│   ├── 09-sessions.ts                           # sessionId, resume, fork
│   ├── 10-production.ts                         # Tracing, cost, error handling, maxTurns
│   └── 11-mcp-integration.ts                    # External MCP servers

└── examples/
    └── README.md                                # Index of all runnable examples
```

## Library/Dependencies

| Language | Package | Install | Context7 |
|----------|---------|---------|----------|
| Python 3.10+ | `claude-agent-sdk` | `pip install claude-agent-sdk` | `/anthropics/claude-agent-sdk-python` |
| Node.js 18+ | `@anthropic-ai/claude-agent-sdk` | `npm install @anthropic-ai/claude-agent-sdk` | TypeScript docs at same repo |

## Content Design

### Part 0: How LLMs Enable Agents (conceptual, no code)

These sections explain the model-level concepts BEFORE any code. The reader must understand *why* tool use works before learning *how* to code it.

#### 01 — How Language Models Work (simplified)
- Token prediction: the model generates one token at a time
- Context window: the model sees all previous messages
- The model does NOT run code — it generates text that *describes* what tool to call
- Why this matters for agents: the model's output is structured, so we can parse it

#### 02 — Tool Calls Are Just Computer Programs
- A "tool" is anything a computer can execute — there is no restriction
- Examples of what a tool CAN be:
  - Local file operations (read, write, delete files on your disk)
  - Shell commands (run any program installed on your machine)
  - HTTP requests (call any REST API, GraphQL endpoint, or web service)
  - Database queries (PostgreSQL, MongoDB, SQLite, Redis, anything)
  - Browser automation (Playwright, Puppeteer — click, type, scrape)
  - Hardware control (GPIO pins, serial ports, USB devices, robots)
  - Email/Slack/Teams (send messages, notifications, alerts)
  - Cloud services (AWS, GCP, Azure — anything with an SDK or API)
  - Local programs that use the internet (your Python script that calls OpenAI, your Node app that streams video)
  - Programs you wrote, programs someone else wrote, system utilities
- The model doesn't care WHERE or HOW the tool runs — it only generates the request (name + arguments as JSON)
- YOU decide what tools to give the model and HOW they execute
- This is the fundamental insight: the model is a reasoning engine, the tools are the hands that do real work in the real world

#### 02 — Tool Use at the Model Level
- You send a prompt + tool definitions (JSON Schema) to the API
- The model can output a special `tool_use` content block instead of plain text
- The model chooses which tool to call and with what arguments
- The model does NOT execute the tool — it only *requests* execution
- We (the SDK/app) execute the tool and send the result back
- Tools can be anything: file I/O, shell commands, HTTP requests, database queries, hardware control, browser automation — local or remote

#### 03 — The Agentic Loop Explained
- This is the core insight: the loop is just repeated tool calls
- Step 1: Send prompt → Model responds
- Step 2: Check `stop_reason`:
  - `"end_turn"` → Model is done, no more tool calls needed
  - `"tool_use"` → Model wants to call a tool, we must execute it and continue
- Step 3: If `tool_use`:
  - Extract `ToolUseBlock` (tool name + arguments)
  - Execute the tool — this is YOUR code running a real computer program (local or remote)
  - Append `ToolResultBlock` with the tool's output
  - Go back to Step 1
- Step 4: If `end_turn` → return final response
- The SDK (`query()`) does this automatically — `ClaudeSDKClient` gives you manual control
- Key insight: the model is the brain deciding WHAT to do, your tools are the hands actually DOING it

#### 04 — Message Protocol
- Every message has `role` (user/assistant) and `content` (array of blocks)
- Block types:
  - `TextBlock` — plain text the model generates for you to read
  - `ToolUseBlock` — model requesting a tool call: `{name, arguments, id}`
  - `ToolResultBlock` — your tool execution result: `{tool_use_id, content}`
  - `ThinkingBlock` — model's reasoning (when extended thinking is on)
- `ResultMessage` — metadata after the loop ends: `stop_reason`, `cost`, `num_turns`, `terminal_reason`
- The flow: `TextBlock` or `ToolUseBlock` → you execute tool → `ToolResultBlock` → model continues

### Part 1: Python Track

#### 01 — Hello Agent
```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for msg in query(
        prompt="Say hello in 3 languages",
        options=ClaudeAgentOptions(allowed_tools=[])
    ):
        print(msg)

asyncio.run(main())
```
**Explanation:** Installing SDK, setting `ANTHROPIC_API_KEY`, what `query()` returns (async stream of messages), why `allowed_tools=[]` means no tools.

#### 02 — The Agentic Loop in Action
```python
import asyncio
from claude_agent_sdk import (
    query, ClaudeAgentOptions,
    AssistantMessage, TextBlock, ToolUseBlock, ToolResultBlock, ResultMessage
)

async def main():
    async for msg in query(
        prompt="Read the README and summarize it",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Glob"])
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"[TEXT] {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"[TOOL_USE] {block.name}({block.arguments})")
                    # SDK executes tool internally and appends ToolResultBlock
        elif isinstance(msg, ResultMessage):
            print(f"\n--- DONE ---")
            print(f"stop_reason: {msg.stop_reason}")
            print(f"terminal_reason: {msg.terminal_reason}")
            print(f"num_turns: {msg.num_turns}")
            print(f"cost: ${msg.total_cost_usd:.4f}")

asyncio.run(main())
```
**Explanation:** Walking through what happens at each message. The SDK runs the loop internally — we just observe. Show the console output of a real run: alternating `TOOL_USE` → (SDK executes) → `TEXT` → `TOOL_USE` → ... → `end_turn`.

#### 03 — Built-in Tools
```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for msg in query(
        prompt="Find all Python files and count lines in each",
        options=ClaudeAgentOptions(
            allowed_tools=["Glob", "Read", "Bash"],
            permission_mode="acceptEdits"
        )
    ):
        if hasattr(msg, "result"):
            print(msg.result)

asyncio.run(main())
```
**Explanation:** What each tool does, `allowed_tools` vs `permission_mode`, how the model decides which tool to use.

#### 04 — Custom Tools
```python
import asyncio
from claude_agent_sdk import (
    tool, create_sdk_mcp_server, query, ClaudeAgentOptions
)

@tool("calculate", "Evaluate a math expression safely", {"expression": str})
async def calculate(args):
    try:
        result = eval(args["expression"])
        return {"content": [{"type": "text", "text": str(result)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {e}"}]}

@tool("get_weather", "Get current weather for a city", {"city": str})
async def get_weather(args):
    return {"content": [{"type": "text", "text": f"Weather in {args['city']}: 72°F sunny"}]}

async def main():
    server = create_sdk_mcp_server("mytools", tools=[calculate, get_weather])
    async for msg in query(
        prompt="What's 15 * 7 + 3? Also, what's the weather in NYC?",
        options=ClaudeAgentOptions(
            mcp_servers={"mytools": server},
            allowed_tools=["mcp__mytools__*"]
        )
    ):
        if hasattr(msg, "result"):
            print(msg.result)

asyncio.run(main())
```
**Explanation:** The `@tool` decorator registers a function with name, description, and JSON Schema args. `create_sdk_mcp_server` makes them available via MCP. Tool naming convention: `mcp__<server>__<tool>`. These tools are just Python functions — they could call APIs, query databases, control hardware, or anything else a computer can do.

#### 05 — Bidirectional Streaming
```python
import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient, ClaudeAgentOptions,
    AssistantMessage, TextBlock, ToolUseBlock
)

async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep"],
        permission_mode="acceptEdits"
    )
    async with ClaudeSDKClient(options) as client:
        await client.connect(prompt="What files are in the current directory?")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")
                    elif isinstance(block, ToolUseBlock):
                        print(f"Tool: {block.name}")
        
        # Session persists — follow-up has full context
        await client.query("Now read the main file and explain it")
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

asyncio.run(main())
```
**Explanation:** `ClaudeSDKClient` vs `query()`: client gives you session persistence, multiple `query()` calls in one session, and (in advanced use) manual tool execution.

#### 06 — Hooks
```python
import asyncio
from datetime import datetime
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher

async def log_tool_use(input_data, tool_use_id, context):
    tool_name = input_data.get("tool_name", "unknown")
    with open("tool_log.txt", "a") as f:
        f.write(f"{datetime.now()}: {tool_name}\n")
    return {}

async def main():
    async for msg in query(
        prompt="Create a file called test.py with hello world",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Write", "Edit"],
            permission_mode="acceptEdits",
            hooks={
                "PostToolUse": [
                    HookMatcher(matcher="Write|Edit", hooks=[log_tool_use])
                ]
            }
        )
    ):
        if hasattr(msg, "result"):
            print(msg.result)

asyncio.run(main())
```
**Explanation:** Hooks let you intercept tool calls. `PreToolUse` fires before execution (can block/modify), `PostToolUse` fires after (can log/validate). `HookMatcher` uses regex on tool names.

#### 07 — Permissions
```python
import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient, ClaudeAgentOptions,
    PermissionResultDeny, ToolPermissionContext
)

async def safety_check(tool_name, tool_input, context: ToolPermissionContext):
    if tool_name == "Bash" and any(
        cmd in str(tool_input) for cmd in ["rm -rf", "sudo", "chmod 777"]
    ):
        return PermissionResultDeny(
            behavior="deny",
            message="Dangerous command blocked by safety policy",
            interrupt=True
        )
    return {"behavior": "allow"}

async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Bash", "Read", "Write"],
        can_use_tool=safety_check
    )
    async with ClaudeSDKClient(options) as client:
        await client.connect(prompt="Run: ls -la")
        async for msg in client.receive_response():
            print(msg)

asyncio.run(main())
```
**Explanation:** `can_use_tool` is the SDK's permission gate. It runs only for tools that would normally prompt the user. Return `PermissionResultDeny` with `interrupt=True` to halt the agent.

#### 08 — Subagents
```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

async def main():
    async for msg in query(
        prompt="Use the security-auditor to check for vulnerabilities, "
               "then use the docs-writer to document findings",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep", "Agent"],
            agents={
                "security-auditor": AgentDefinition(
                    description="Expert security auditor",
                    prompt="Analyze code for security vulnerabilities.",
                    tools=["Read", "Glob", "Grep"]
                ),
                "docs-writer": AgentDefinition(
                    description="Technical documentation writer",
                    prompt="Write clear technical documentation.",
                    tools=["Read", "Write"]
                )
            }
        )
    ):
        if hasattr(msg, "result"):
            print(msg.result)

asyncio.run(main())
```
**Explanation:** Subagents are isolated agents spawned by the main agent. Each has its own tools and system prompt. The main agent delegates tasks via the `Agent` tool. Messages from subagents include `parent_tool_use_id`.

#### 09 — Sessions
```python
import asyncio
from claude_agent_sdk import (
    query, ClaudeAgentOptions, SystemMessage, ResultMessage
)

async def main():
    session_id = None
    
    async for msg in query(
        prompt="Read and analyze auth.py — remember the issues",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Glob"])
    ):
        if isinstance(msg, SystemMessage) and msg.subtype == "init":
            session_id = msg.data["session_id"]
    
    # Resume later — Claude remembers everything from the first conversation
    async for msg in query(
        prompt="Now fix the issues you found",
        options=ClaudeAgentOptions(
            resume=session_id,
            allowed_tools=["Read", "Edit"]
        )
    ):
        if isinstance(msg, ResultMessage):
            print(f"Completed in {msg.num_turns} turns")

asyncio.run(main())
```
**Explanation:** `session_id` captures the conversation context. `resume` continues it later. Claude remembers all files read, analysis done, and conversation history.

#### 10 — Production Patterns
```python
import asyncio
import json
from datetime import datetime
from claude_agent_sdk import (
    query, ClaudeAgentOptions, AssistantMessage, ResultMessage,
    TextBlock, ToolUseBlock
)

async def run_agent(prompt: str, max_turns: int = 10) -> dict:
    trace = {"start": datetime.now().isoformat(), "prompt": prompt, "turns": []}
    
    try:
        async for msg in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                allowed_tools=["Read", "Edit", "Bash", "Glob", "Grep"],
                permission_mode="acceptEdits",
                max_turns=max_turns
            )
        ):
            if isinstance(msg, AssistantMessage):
                turn = {"blocks": []}
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        turn["blocks"].append({"type": "text", "text": block.text})
                    elif isinstance(block, ToolUseBlock):
                        turn["blocks"].append({
                            "type": "tool_use", "name": block.name,
                            "args": block.arguments
                        })
                trace["turns"].append(turn)
            elif isinstance(msg, ResultMessage):
                trace["result"] = {
                    "stop_reason": msg.stop_reason,
                    "cost_usd": msg.total_cost_usd,
                    "num_turns": msg.num_turns,
                    "terminal_reason": msg.terminal_reason
                }
    except Exception as e:
        trace["error"] = str(e)
    
    trace["end"] = datetime.now().isoformat()
    return trace

async def main():
    trace = await run_agent("Find and fix the bug in auth.py")
    with open("agent_trace.json", "w") as f:
        json.dump(trace, f, indent=2)
    print(f"Completed: {trace['result']}")

asyncio.run(main())
```
**Explanation:** `max_turns` limits the loop. `terminal_reason` tells you why it stopped. Full tracing for debugging and cost control.

#### 11 — External MCP Servers
```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for msg in query(
        prompt="Open example.com and extract the main heading",
        options=ClaudeAgentOptions(
            mcp_servers={
                "playwright": {
                    "command": "npx",
                    "args": ["@playwright/mcp@latest"]
                }
            },
            allowed_tools=["mcp__playwright__*"]
        )
    ):
        if hasattr(msg, "result"):
            print(msg.result)

asyncio.run(main())
```
**Explanation:** MCP (Model Context Protocol) lets you connect any external tool server — local or remote. Wildcard `mcp__playwright__*` allows all tools from that server. Tools can run on your machine, on a server, or across the internet.

---

### Part 2: Node.js/TypeScript Track

#### 01 — Hello Agent
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const msg of query({
  prompt: "Say hello in 3 languages",
  options: { allowedTools: [] }
})) {
  console.log(msg);
}
```
**Explanation:** Same concept as Python but using `for await...of`. Top-level await in ES modules. TypeScript types for messages.

#### 02 — The Agentic Loop in Action
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";
import type { AssistantMessage, ResultMessage } from "@anthropic-ai/claude-agent-sdk";

for await (const msg of query({
  prompt: "Read the README and summarize it",
  options: { allowedTools: ["Read", "Glob"] }
})) {
  if (msg.type === "assistant") {
    for (const block of msg.content) {
      if (block.type === "text") {
        console.log(`[TEXT] ${block.text}`);
      } else if (block.type === "tool_use") {
        console.log(`[TOOL_USE] ${block.name}(${JSON.stringify(block.arguments)})`);
      }
    }
  } else if (msg.type === "result") {
    console.log(`\n--- DONE ---`);
    console.log(`stop_reason: ${msg.stop_reason}`);
    console.log(`terminal_reason: ${msg.terminal_reason}`);
    console.log(`num_turns: ${msg.num_turns}`);
    console.log(`cost: $${msg.total_cost_usd?.toFixed(4)}`);
  }
}
```
**Explanation:** Message type checking with `msg.type` discriminator. Content block type narrowing. Same loop concepts as Python.

#### 03 — Built-in Tools
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const msg of query({
  prompt: "Find all TypeScript files and count lines in each",
  options: {
    allowedTools: ["Glob", "Read", "Bash"],
    permissionMode: "acceptEdits"
  }
})) {
  if ("result" in msg) console.log(msg.result);
}
```
**Explanation:** Same tools, camelCase options in TypeScript. `permissionMode` auto-accepts file edits.

#### 04 — Custom Tools
```typescript
import { query, tool, createMcpServer } from "@anthropic-ai/claude-agent-sdk";

const calculate = tool(
  "calculate",
  "Evaluate a math expression safely",
  { expression: { type: "string" } },
  async (args) => {
    try {
      const result = Function(`"use strict"; return (${args.expression})`)();
      return { content: [{ type: "text" as const, text: String(result) }] };
    } catch (e) {
      return { content: [{ type: "text" as const, text: `Error: ${e}` }] };
    }
  }
);

const getWeather = tool(
  "get_weather",
  "Get current weather for a city",
  { city: { type: "string" } },
  async (args) => ({
    content: [{ type: "text" as const, text: `Weather in ${args.city}: 72°F sunny` }]
  })
);

const server = createMcpServer("mytools", [calculate, getWeather]);

for await (const msg of query({
  prompt: "What's 15 * 7 + 3? Also, what's the weather in NYC?",
  options: {
    mcpServers: { mytools: server },
    allowedTools: ["mcp__mytools__*"]
  }
})) {
  if ("result" in msg) console.log(msg.result);
}
```
**Explanation:** `tool()` function with name, description, JSON Schema args, and async handler. `createMcpServer()` wraps tools into an MCP server. These are just TypeScript/JavaScript functions — they can call any API, run any command, control any service.

#### 05 — Bidirectional Streaming
```typescript
import { ClaudeSDKClient } from "@anthropic-ai/claude-agent-sdk";

const client = new ClaudeSDKClient({
  allowedTools: ["Read", "Glob", "Grep"],
  permissionMode: "acceptEdits"
});

await client.connect({ prompt: "What files are in the current directory?" });
for await (const msg of client.receiveResponse()) {
  if (msg.type === "assistant") {
    for (const block of msg.content) {
      if (block.type === "text") console.log(`Claude: ${block.text}`);
      else if (block.type === "tool_use") console.log(`Tool: ${block.name}`);
    }
  }
}

// Session persists
await client.query("Now read the main file and explain it");
for await (const msg of client.receiveResponse()) {
  if (msg.type === "assistant") {
    for (const block of msg.content) {
      if (block.type === "text") console.log(`Claude: ${block.text}`);
    }
  }
}

await client.disconnect();
```
**Explanation:** `ClaudeSDKClient` class with `connect()`, `query()`, `receiveResponse()`, `disconnect()`. Session context persists across queries.

#### 06 — Hooks
```typescript
import { query, hookMatcher } from "@anthropic-ai/claude-agent-sdk";
import { appendFileSync } from "fs";

const logToolUse = async (input: any, toolUseId: string, context: any) => {
  const toolName = input?.tool_name ?? "unknown";
  appendFileSync("tool_log.txt", `${new Date().toISOString()}: ${toolName}\n`);
  return {};
};

for await (const msg of query({
  prompt: "Create a file called test.ts with hello world",
  options: {
    allowedTools: ["Read", "Write", "Edit"],
    permissionMode: "acceptEdits",
    hooks: {
      PostToolUse: [hookMatcher("Write|Edit", [logToolUse])]
    }
  }
})) {
  if ("result" in msg) console.log(msg.result);
}
```
**Explanation:** `hookMatcher()` creates a matcher with regex pattern and callback array. Same hook events as Python.

#### 07 — Permissions
```typescript
import { ClaudeSDKClient } from "@anthropic-ai/claude-agent-sdk";

const safetyCheck = async (toolName: string, toolInput: any, context: any) => {
  if (toolName === "Bash" && ["rm -rf", "sudo", "chmod 777"].some(
    cmd => String(toolInput).includes(cmd)
  )) {
    return {
      behavior: "deny" as const,
      message: "Dangerous command blocked",
      interrupt: true
    };
  }
  return { behavior: "allow" as const };
};

const client = new ClaudeSDKClient({
  allowedTools: ["Bash", "Read", "Write"],
  canUseTool: safetyCheck
});

await client.connect({ prompt: "Run: ls -la" });
for await (const msg of client.receiveResponse()) {
  console.log(msg);
}
await client.disconnect();
```
**Explanation:** `canUseTool` callback with same semantics. Return `deny` with `interrupt: true` to halt.

#### 08 — Subagents
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const msg of query({
  prompt: "Use the security-auditor to check for vulnerabilities",
  options: {
    allowedTools: ["Read", "Glob", "Grep", "Agent"],
    agents: {
      "security-auditor": {
        description: "Expert security auditor",
        prompt: "Analyze code for security vulnerabilities.",
        tools: ["Read", "Glob", "Grep"]
      },
      "docs-writer": {
        description: "Technical documentation writer",
        prompt: "Write clear technical documentation.",
        tools: ["Read", "Write"]
      }
    }
  }
})) {
  if ("result" in msg) console.log(msg.result);
}
```
**Explanation:** `agents` object in options defines subagents. Each gets isolated context and tool access.

#### 09 — Sessions
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

let sessionId: string | undefined;

for await (const msg of query({
  prompt: "Read and analyze auth.py — remember the issues",
  options: { allowedTools: ["Read", "Glob"] }
})) {
  if (msg.type === "system" && msg.subtype === "init") {
    sessionId = msg.session_id;
  }
}

// Resume later
for await (const msg of query({
  prompt: "Now fix the issues you found",
  options: { resume: sessionId, allowedTools: ["Read", "Edit"] }
})) {
  if (msg.type === "result") {
    console.log(`Completed in ${msg.num_turns} turns`);
  }
}
```
**Explanation:** `session_id` from init message, `resume` option to continue. Same pattern as Python.

#### 10 — Production Patterns
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";
import { writeFileSync } from "fs";

interface AgentTrace {
  start: string;
  prompt: string;
  turns: any[];
  result?: any;
  error?: string;
  end?: string;
}

async function runAgent(prompt: string, maxTurns: number = 10): Promise<AgentTrace> {
  const trace: AgentTrace = { start: new Date().toISOString(), prompt, turns: [] };
  
  try {
    for await (const msg of query({
      prompt,
      options: {
        allowedTools: ["Read", "Edit", "Bash", "Glob", "Grep"],
        permissionMode: "acceptEdits",
        maxTurns
      }
    })) {
      if (msg.type === "assistant") {
        const turn = { blocks: msg.content.map((b: any) => ({
          type: b.type, text: b.text, name: b.name, args: b.arguments
        }))};
        trace.turns.push(turn);
      } else if (msg.type === "result") {
        trace.result = {
          stopReason: msg.stop_reason,
          costUsd: msg.total_cost_usd,
          numTurns: msg.num_turns,
          terminalReason: msg.terminal_reason
        };
      }
    }
  } catch (e) {
    trace.error = String(e);
  }
  
  trace.end = new Date().toISOString();
  return trace;
}

const trace = await runAgent("Find and fix the bug in auth.ts");
writeFileSync("agent_trace.json", JSON.stringify(trace, null, 2));
console.log(`Completed: ${trace.result}`);
```
**Explanation:** `maxTurns` option, `terminal_reason` for debugging, JSONL tracing.

#### 11 — External MCP Servers
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const msg of query({
  prompt: "Open example.com and extract the main heading",
  options: {
    mcpServers: {
      playwright: { command: "npx", args: ["@playwright/mcp@latest"] }
    },
    allowedTools: ["mcp__playwright__*"]
  }
})) {
  if ("result" in msg) console.log(msg.result);
}
```
**Explanation:** Same MCP pattern, object syntax for servers in TypeScript. Tools can be local processes or remote HTTP endpoints.

## Verification
- [ ] All Python examples run with `ANTHROPIC_API_KEY` set
- [ ] All Node.js examples run with `ANTHROPIC_API_KEY` set
- [ ] Conceptual sections explain WHY before HOW
- [ ] Tutorial is readable top-to-bottom with clear progression
- [ ] Every concept is demonstrated with working code in both languages
- [ ] README links to all sections
- [ ] `examples/README.md` lists all runnable scripts with commands