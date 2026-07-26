# The Message Protocol

This document explains the data structures that flow through the agentic loop. Understanding these types helps you read the code examples and build your own agents.

## Message Types

The SDK defines several message types. Each one represents a different kind of event in the conversation:

### UserMessage
What YOU send to the model.

```python
# Python
UserMessage(content="Read auth.py and fix the bug")
```

```typescript
// TypeScript
{ role: "user", content: "Read auth.py and fix the bug" }
```

### AssistantMessage
What THE MODEL generates. This is the most important message type — it contains the model's response, which can include text, tool calls, or both.

```python
# Python
AssistantMessage(content=[
    TextBlock(text="I'll read the file first..."),
    ToolUseBlock(name="Read", arguments={"file_path": "auth.py"}, id="toolu_abc123")
])
```

```typescript
// TypeScript
{
  type: "assistant",
  content: [
    { type: "text", text: "I'll read the file first..." },
    { type: "tool_use", name: "Read", arguments: { file_path: "auth.py" }, id: "toolu_abc123" }
  ]
}
```

### ToolResultBlock
What YOU send back after executing a tool. This is how the model gets the results of its tool calls.

```python
# Python
ToolResultBlock(tool_use_id="toolu_abc123", content="def authenticate(user):\n    ...")
```

```typescript
// TypeScript
{ type: "tool_result", tool_use_id: "toolu_abc123", content: "def authenticate(user):\n    ..." }
```

### ResultMessage
Metadata after the loop ends. Contains cost, usage, and why the loop stopped.

```python
# Python
ResultMessage(
    stop_reason="end_turn",
    terminal_reason="completed",
    num_turns=3,
    total_cost_usd=0.0042,
    session_id="ses_abc123"
)
```

```typescript
// TypeScript
{
  type: "result",
  stop_reason: "end_turn",
  terminal_reason: "completed",
  num_turns: 3,
  total_cost_usd: 0.0042,
  session_id: "ses_abc123"
}
```

### SystemMessage
Internal events from the SDK, like session initialization.

```python
# Python
SystemMessage(subtype="init", data={"session_id": "ses_abc123"})
```

## Content Blocks

Every `AssistantMessage` has a `content` array. Each element is a **content block**. There are four main types:

### TextBlock
Plain text the model generates for you to read.

```python
TextBlock(text="I found a security vulnerability on line 5...")
```

### ToolUseBlock
The model requesting that YOUR code execute a tool.

```python
ToolUseBlock(
    name="Read",                          # which tool to call
    arguments={"file_path": "auth.py"},   # arguments as a dict
    id="toolu_abc123"                     # unique ID for this call
)
```

The `id` field is critical — it links the tool call to its result. When you execute the tool, you must include this `id` in the `ToolResultBlock` so the model knows which result corresponds to which call.

### ToolResultBlock
Your tool's output, sent back to the model.

```python
ToolResultBlock(
    tool_use_id="toolu_abc123",   # matches the ToolUseBlock.id
    content="def authenticate(user):\n    ..."  # string result
)
```

### ThinkingBlock
The model's internal reasoning (when extended thinking is enabled).

```python
ThinkingBlock(text="Let me analyze this code... I see a SQL injection risk...")
```

## The Complete Flow

Here's how all these types work together in one agentic loop iteration:

```
YOU send:
  UserMessage(content="What files are in src/?")
  
MODEL responds:
  AssistantMessage(content=[
      ToolUseBlock(name="Glob", arguments={"pattern": "src/**/*"}, id="toolu_001")
  ])
  stop_reason: "tool_use"

YOU execute the Glob tool and send:
  ToolResultBlock(tool_use_id="toolu_001", content="src/app.py\nsrc/utils.py\nsrc/auth.py")

MODEL responds:
  AssistantMessage(content=[
      TextBlock(text="There are 3 files in src/: app.py, utils.py, and auth.py.")
  ])
  stop_reason: "end_turn"

Loop ends. Final answer delivered.
```

## What Flows Where

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  YOUR CODE   │────►│    MODEL     │────►│  YOUR CODE   │
│  (UserMsg)   │     │ (AssistantMsg)│     │ (ToolResult) │
└─────────────┘     └─────────────┘     └─────────────┘
      ▲                                        │
      │                                        │
      └────────────────────────────────────────┘
                    (loop continues)
```

## Key Takeaway

The message protocol is simple:
- You send text (UserMessage)
- Model responds with text or tool requests (AssistantMessage with content blocks)
- If tool request → you execute and send result (ToolResultBlock)
- Model responds again → repeat until `stop_reason` is `"end_turn"`

Everything in the agentic loop is just messages flowing back and forth between your code and the model.

## Next

Now that you understand the fundamentals, start building. Choose your track:
- [Python Track](../01-python/README.md)
- [Node.js Track](../02-nodejs/README.md)
