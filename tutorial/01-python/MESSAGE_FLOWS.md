# Claude Agent SDK — Message Flows

Complete reference for every message type, flow pattern, and state transition in the Claude Agent SDK. Each section includes a Mermaid diagram showing the exact sequence of messages.

---

## Table of Contents

1. [Message Types](#message-types)
2. [Flow 1: Simple Query (No Tools)](#flow-1-simple-query-no-tools)
3. [Flow 2: Tool Use (Single Turn)](#flow-2-tool-use-single-turn)
4. [Flow 3: Multi-Turn Tool Loop](#flow-3-multi-turn-tool-loop)
5. [Flow 4: Error Handling](#flow-4-error-handling)
6. [Flow 5: Session Resume (Memory)](#flow-5-session-resume-memory)
7. [Flow 6: Hooks Lifecycle](#flow-6-hooks-lifecycle)
8. [Flow 7: Rate Limiting](#flow-7-rate-limiting)
9. [Flow 8: Streaming with Subagents](#flow-8-streaming-with-subagents)
10. [State Diagram: stop_reason Transitions](#state-diagram-stop_reason-transitions)
11. [Complete Message Reference](#complete-message-reference)

---

## Message Types

Every message yielded by `query()` or `query_stream()` is one of these types:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SDK Message Types                           │
├─────────────────────┬───────────────────────────────────────────────┤
│ HookEventMessage    │ Hook lifecycle (started / response)           │
│ SystemMessage       │ Session init, thinking tokens, status         │
│ AssistantMessage    │ Model output (text, tool_use, thinking)       │
│ UserMessage         │ Tool results returned to model                │
│ RateLimitEvent      │ Rate limit status updates                     │
│ ResultMessage       │ Final message — contains cost, session_id     │
└─────────────────────┴───────────────────────────────────────────────┘
```

### Message Fields

#### HookEventMessage

| Field | Type | Description |
|-------|------|-------------|
| `subtype` | `"hook_started"` \| `"hook_response"` | Hook lifecycle phase |
| `data` | `dict` | Full hook payload (hook_id, hook_name, hook_event, output, stdout, stderr, exit_code, outcome) |
| `hook_event_name` | `str` | Event type: `SessionStart`, `PreToolUse`, `PostToolUse`, etc. |
| `session_id` | `str` | Session this hook belongs to |
| `uuid` | `str` | Unique message ID |

#### SystemMessage

| Field | Type | Description |
|-------|------|-------------|
| `subtype` | `"init"` \| `"thinking_tokens"` \| ... | System event type |
| `data` | `dict` | Event payload — for `init`: cwd, session_id, tools, model, etc. |
| `session_id` | `str` | Session ID (in data dict) |

#### AssistantMessage

| Field | Type | Description |
|-------|------|-------------|
| `content` | `list[Block]` | `TextBlock`, `ToolUseBlock`, or `ThinkingBlock` |
| `model` | `str` | Model used (e.g., `"claude-sonnet-5"`) |
| `stop_reason` | `None` \| `"end_turn"` \| `"tool_use"` | `None` while streaming, final value at end |
| `usage` | `dict` | Token counts (input, output, cache) |
| `message_id` | `str` | API message ID |
| `session_id` | `str` | Session this message belongs to |
| `uuid` | `str` | Unique message ID |

#### UserMessage

| Field | Type | Description |
|-------|------|-------------|
| `content` | `list[ToolResultBlock]` | Tool execution results |
| `uuid` | `str` | Unique message ID |
| `parent_tool_use_id` | `str` \| `None` | Links to the AssistantMessage tool call |
| `tool_use_result` | `dict` | Tool execution metadata (stdout, stderr, exit_code, etc.) |

#### RateLimitEvent

| Field | Type | Description |
|-------|------|-------------|
| `rate_limit_info` | `RateLimitInfo` | Status, utilization, resets_at, overage_status |
| `uuid` | `str` | Unique message ID |
| `session_id` | `str` | Session ID |

#### ResultMessage

| Field | Type | Description |
|-------|------|-------------|
| `subtype` | `"success"` \| `"error"` | Final outcome |
| `stop_reason` | `"end_turn"` \| `"max_turns"` \| `"max_tokens"` \| `"error"` | Why the agent stopped |
| `terminal_reason` | `"completed"` \| `"aborted"` \| ... | Terminal state reason |
| `num_turns` | `int` | Number of agentic loop iterations |
| `total_cost_usd` | `float` | Total API cost |
| `session_id` | `str` | Session ID (use for resume) |
| `duration_ms` | `int` | Wall clock time |
| `duration_api_ms` | `int` | API time only |
| `usage` | `dict` | Aggregated token usage |
| `result` | `str` | Final text output |
| `errors` | `list` \| `None` | Any errors encountered |

---

## Flow 1: Simple Query (No Tools)

The most basic flow — user sends a prompt, model responds with text.

```mermaid
sequenceDiagram
    participant U as User
    participant S as SDK
    participant A as API

    U->>S: query("Say hello in 3 languages")
    S->>A: POST /messages

    Note over A: Hook: SessionStart

    A-->>S: HookEventMessage (hook_started)
    Note right of S: subtype: "hook_started"<br/>hook_event: "SessionStart"

    A-->>S: HookEventMessage (hook_response)
    Note right of S: subtype: "hook_response"<br/>exit_code: 0<br/>output: {...}

    A-->>S: SystemMessage (init)
    Note right of S: subtype: "init"<br/>session_id, tools, model,<br/>mcp_servers, skills, etc.

    A-->>S: SystemMessage (thinking_tokens)
    Note right of S: estimated_tokens: 50

    A-->>S: AssistantMessage
    Note right of S: content: [TextBlock]<br/>text: "Hello!Bonjour!..."

    A-->>S: RateLimitEvent
    Note right of S: status: "allowed"<br/>utilization: 0.12

    A-->>S: ResultMessage
    Note right of S: subtype: "success"<br/>stop_reason: "end_turn"<br/>total_cost_usd: 0.16

    S-->>U: (stream complete)
```

**Key characteristics:**
- Single `AssistantMessage` with only `TextBlock`
- `stop_reason` goes from `None` (streaming) to `"end_turn"` (final)
- No `ToolUseBlock` — model didn't request any tools

---

## Flow 2: Tool Use (Single Turn)

Model requests a tool, SDK executes it, model processes the result.

```mermaid
sequenceDiagram
    participant U as User
    participant S as SDK
    participant A as API
    participant T as Tool

    U->>S: query("Read pyproject.toml")
    S->>A: POST /messages

    Note over A: Hook: SessionStart

    A-->>S: HookEventMessage (hook_started)
    A-->>S: HookEventMessage (hook_response)
    A-->>S: SystemMessage (init)
    A-->>S: SystemMessage (thinking_tokens)

    A-->>S: AssistantMessage
    Note right of S: content: [ToolUseBlock]<br/>name: "Read"<br/>input: {file: "pyproject.toml"}

    Note over S: stop_reason: "tool_use"<br/>→ execute tool

    S->>T: Read("pyproject.toml")
    T-->>S: file contents

    S-->>U: (ToolUseBlock displayed)

    S->>A: UserMessage
    Note right of S: content: [ToolResultBlock]<br/>tool_use_id: "toolu_01..."<br/>content: "file contents..."

    A-->>S: AssistantMessage
    Note right of S: content: [TextBlock]<br/>text: "The file contains..."

    A-->>S: ResultMessage
    Note right of S: stop_reason: "end_turn"<br/>num_turns: 2<br/>total_cost_usd: 0.03

    S-->>U: (stream complete)
```

**Key characteristics:**
- `AssistantMessage` contains `ToolUseBlock` (not `TextBlock`)
- SDK sends `UserMessage` with `ToolResultBlock` back to API
- Second `AssistantMessage` contains the final text response
- `num_turns: 2` in `ResultMessage` (one tool use = two turns)

---

## Flow 3: Multi-Turn Tool Loop

Model uses multiple tools in sequence before responding.

```mermaid
sequenceDiagram
    participant U as User
    participant S as SDK
    participant A as API
    participant T as Tools

    U->>S: query("Find all Python files and count lines")

    loop Agentic Loop
        S->>A: POST /messages
        A-->>S: AssistantMessage (ToolUseBlock)
        Note right of S: Tool: Glob *.py

        S->>T: Glob("*.py")
        T-->>S: ["file1.py", "file2.py", ...]

        S->>A: UserMessage (ToolResultBlock)
        A-->>S: AssistantMessage (ToolUseBlock)
        Note right of S: Tool: Read file1.py

        S->>T: Read("file1.py")
        T-->>S: file content

        S->>A: UserMessage (ToolResultBlock)
        A-->>S: AssistantMessage (ToolUseBlock)
        Note right of S: Tool: Read file2.py

        S->>T: Read("file2.py")
        T-->>S: file content

        S->>A: UserMessage (ToolResultBlock)
    end

    A-->>S: AssistantMessage
    Note right of S: content: [TextBlock]<br/>"Found 3 files with 450 total lines"

    A-->>S: ResultMessage
    Note right of S: num_turns: 6<br/>stop_reason: "end_turn"

    S-->>U: (stream complete)
```

**Key characteristics:**
- Loop continues until model returns `TextBlock` (stop_reason: `"end_turn"`)
- Each tool call adds 2 to `num_turns`
- `max_turns` option can break the loop early

---

## Flow 4: Error Handling

Multiple error scenarios and how the SDK handles them.

```mermaid
sequenceDiagram
    participant U as User
    participant S as SDK
    participant A as API

    U->>S: query("Do something dangerous")

    alt API Error (rate limit, auth, etc.)
        A-->>S: ResultMessage
        Note right of S: subtype: "error"<br/>stop_reason: "error"<br/>is_error: true<br/>errors: ["rate_limit_exceeded"]

        S-->>U: (error displayed)

    else Tool Execution Error
        A-->>S: AssistantMessage (ToolUseBlock)
        Note right of S: Tool: Bash("rm -rf /")

        S-->>S: Tool execution fails
        S->>A: UserMessage
        Note right of S: content: [ToolResultBlock]<br/>is_error: true<br/>content: "Permission denied"

        A-->>S: AssistantMessage
        Note right of S: "I can't do that.<br/>Here's what I can help with..."

        A-->>S: ResultMessage
        Note right of S: subtype: "success"<br/>stop_reason: "end_turn"
    end
```

### Error Fields

| Field | Location | Description |
|-------|----------|-------------|
| `is_error` | `ResultMessage` | `true` if the run failed |
| `errors` | `ResultMessage` | List of error strings |
| `api_error_status` | `ResultMessage` | API-level error info |
| `is_error` | `ToolResultBlock` | `true` if tool execution failed |

---

## Flow 5: Session Resume (Memory)

Using `session_id` to maintain context across separate API calls.

```mermaid
sequenceDiagram
    participant U as User
    participant S as SDK
    participant A as API

    Note over U,A: ─── Turn 1: Establish Context ───

    U->>S: query("My name is Carlos")
    S->>A: POST /messages (new session)
    A-->>S: SystemMessage (init)
    Note right of S: session_id: "abc-123..."

    A-->>S: AssistantMessage
    Note right of S: "Nice to meet you,<br/>Carlos!"

    A-->>S: ResultMessage
    Note right of S: session_id: "abc-123..."<br/>terminal_reason: "completed"

    Note over U,A: ─── Turn 2: Resume Session ───

    U->>S: query("What's my name?")
    Note over S: options.resume = "abc-123..."

    S->>A: POST /messages (resume session)
    A-->>S: SystemMessage (init)
    Note right of S: session_id: "abc-123..."<br/>(same session)

    A-->>S: AssistantMessage
    Note right of S: "Your name is Carlos."

    A-->>S: ResultMessage
    Note right of S: session_id: "abc-123..."<br/>(context preserved)
```

**Key points:**
- `session_id` appears in `SystemMessage(init)` and `ResultMessage`
- Pass `session_id` via `ClaudeAgentOptions(resume=session_id)`
- Without resume, each `query()` is a fresh session (no memory)

---

## Flow 6: Hooks Lifecycle

Hooks fire at specific points in the agent lifecycle.

```mermaid
sequenceDiagram
    participant S as SDK
    participant H as Hook
    participant A as API

    Note over S,A: ─── Session Start ───

    S->>H: SessionStart:startup hook
    H-->>S: HookEventMessage (hook_started)
    H-->>S: HookEventMessage (hook_response)
    Note right of S: exit_code: 0<br/>output: {additionalContext: "..."}

    Note over S,A: ─── Before Tool Use ───

    S->>A: POST /messages
    A-->>S: AssistantMessage (ToolUseBlock)

    S->>H: PreToolUse hook
    H-->>S: HookEventMessage (hook_started)
    Note right of S: hook_event: "PreToolUse"<br/>tool_name: "Read"<br/>tool_input: {...}

    H-->>S: HookEventMessage (hook_response)
    Note right of S: decision: "allow"<br/>or "block"

    Note over S,A: ─── Tool Execution ───

    S->>S: Execute tool
    S->>A: UserMessage (ToolResultBlock)

    Note over S,A: ─── After Tool Use ───

    S->>H: PostToolUse hook
    H-->>S: HookEventMessage (hook_started)
    Note right of S: hook_event: "PostToolUse"

    H-->>S: HookEventMessage (hook_response)

    Note over S,A: ─── Session End ───

    A-->>S: ResultMessage
    S->>H: SessionEnd hook
    H-->>S: HookEventMessage (hook_started)
    H-->>S: HookEventMessage (hook_response)
```

### Hook Events

| Event | When | Purpose |
|-------|------|---------|
| `SessionStart` | Session begins | Load skills, inject context |
| `PreToolUse` | Before tool execution | Allow/block/modify tool calls |
| `PostToolUse` | After tool execution | Log, modify results |
| `SessionEnd` | Session completes | Cleanup, final logging |

---

## Flow 7: Rate Limiting

Rate limit events and how they affect the flow.

```mermaid
sequenceDiagram
    participant U as User
    participant S as SDK
    participant A as API

    U->>S: query("Complex analysis")

    A-->>S: RateLimitEvent
    Note right of S: status: "allowed"<br/>resets_at: 1785038400<br/>utilization: 0.45

    loop Agentic Loop
        A-->>S: AssistantMessage (ToolUseBlock)
        S->>A: UserMessage (ToolResultBlock)

        A-->>S: RateLimitEvent
        Note right of S: utilization: 0.62
    end

    A-->>S: RateLimitEvent
    Note right of S: status: "allowed"<br/>utilization: 0.78

    A-->>S: AssistantMessage (TextBlock)
    A-->>S: ResultMessage
    Note right of S: stop_reason: "end_turn"
```

### Rate Limit States

| Status | Meaning |
|--------|---------|
| `"allowed"` | Request permitted, continue |
| `"rejected"` | Rate limited, wait for reset |
| `"overage"` | Using overage credits |

---

## Flow 8: Streaming with Subagents

Subagent dispatch and result collection.

```mermaid
sequenceDiagram
    participant U as User
    participant S as SDK
    participant A as API
    participant SA as Subagent

    U->>S: query("Research and implement feature X")

    A-->>S: AssistantMessage
    Note right of S: content: [ToolUseBlock]<br/>name: "Task"<br/>input: {prompt: "Research..."}

    S->>SA: Task (subagent)
    Note over SA: Subagent runs<br/>independently

    loop Subagent Messages
        SA-->>S: SubagentMessage
        Note right of S: Subagent progress updates
    end

    SA-->>S: SubagentResult
    Note right of S: Subagent complete

    S->>A: UserMessage (ToolResultBlock)
    Note right of S: content: [ToolResultBlock]<br/>content: "Research findings..."

    A-->>S: AssistantMessage
    Note right of S: content: [ToolUseBlock]<br/>name: "Write"<br/>input: {file: "x.py", content: "..."}

    S->>A: UserMessage (ToolResultBlock)
    A-->>S: AssistantMessage (TextBlock)
    A-->>S: ResultMessage
```

---

## State Diagram: stop_reason Transitions

How `stop_reason` changes throughout a conversation.

```mermaid
stateDiagram-v2
    [*] --> None: API streaming starts

    None --> None: AssistantMessage chunks arriving
    None --> tool_use: Model requests tool
    None --> end_turn: Model finishes text

    tool_use --> None: Tool executed,<br/>UserMessage sent
    tool_use --> error: Tool fails,<br/>max retries reached

    end_turn --> [*]: ResultMessage

    state "Terminal Reasons" as TR {
        completed --> [*]
        aborted --> [*]
        error --> [*]
    }

    note right of None
        stop_reason = None
        while streaming
    end note

    note right of tool_use
        stop_reason = "tool_use"
        model needs tool execution
    end note

    note right of end_turn
        stop_reason = "end_turn"
        model is done
    end note
```

---

## Complete Message Reference

### Session Initialization Sequence

```
1. HookEventMessage (hook_started)     ← SessionStart hook begins
2. HookEventMessage (hook_response)    ← SessionStart hook completes
3. SystemMessage (init)                ← Session configured (tools, model, cwd, etc.)
```

### Tool Use Sequence

```
4. SystemMessage (thinking_tokens)     ← Model thinking (optional)
5. AssistantMessage                    ← Model output (ToolUseBlock or TextBlock)
6. [RateLimitEvent]                    ← Rate limit status (optional)
7. [UserMessage]                       ← Tool results (if tool was called)
8. Go to step 4                        ← Loop continues until end_turn
```

### Session Termination Sequence

```
9.  ResultMessage                      ← Final result (cost, session_id, stop_reason)
10. [HookEventMessage]                 ← SessionEnd hook (optional)
```

### Message Type Frequency

| Message Type | Frequency | Notes |
|-------------|-----------|-------|
| `HookEventMessage` | 2-6 per session | Always paired (started + response) |
| `SystemMessage` | 1+ per session | `init` always first, `thinking_tokens` per turn |
| `AssistantMessage` | 1+ per turn | Contains `TextBlock`, `ToolUseBlock`, or `ThinkingBlock` |
| `UserMessage` | 0+ per turn | Only when tools are executed |
| `RateLimitEvent` | 0+ per session | Periodic status updates |
| `ResultMessage` | 1 per session | Always the final message |

---

## Appendix: Block Types in AssistantMessage.content

| Block Type | Fields | When Used |
|-----------|--------|-----------|
| `TextBlock` | `text` | Model generating text response |
| `ToolUseBlock` | `id`, `name`, `input` | Model requesting tool execution |
| `ThinkingBlock` | `thinking`, `signature` | Extended thinking / reasoning |

---

## Appendix: ResultMessage.stop_reason Values

| Value | Meaning |
|-------|---------|
| `"end_turn"` | Model finished naturally |
| `"tool_use"` | Model requested a tool (should not appear in final result) |
| `"max_turns"` | Hit the `max_turns` limit |
| `"max_tokens"` | Hit the `max_tokens` limit |
| `"error"` | An error occurred |

---

## Appendix: ResultMessage.terminal_reason Values

| Value | Meaning |
|-------|---------|
| `"completed"` | Normal completion |
| `"aborted"` | User or system aborted |
| `"error"` | Error termination |
| `"timeout"` | Session timed out |
