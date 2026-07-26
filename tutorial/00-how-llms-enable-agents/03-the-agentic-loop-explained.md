# The Agentic Loop

The agentic loop is the engine that makes agents work. It's a simple cycle that repeats until the task is done. Understanding this loop is the single most important concept in this tutorial.

## The Loop in Plain English

```
1. You give the model a task
2. The model thinks about it and decides what to do
3. If it needs to run a tool → it asks you to execute it
4. You run the tool and give it the result
5. The model thinks again with the new information
6. Repeat steps 3-5 until the model says "I'm done"
```

That's it. Every agent — from a simple file reader to a complex autonomous coder — uses this same loop.

## The Technical Details

When you call `query()`, the SDK runs this loop internally:

```
┌─────────────────────────────────────────────────────────────┐
│                      THE AGENTIC LOOP                       │
│                                                             │
│   ┌──────────┐                                              │
│   │  PROMPT   │  "Read auth.py and fix the bug"             │
│   └────┬─────┘                                              │
│        │                                                    │
│        ▼                                                    │
│   ┌──────────────────┐                                      │
│   │  MODEL RESPONDS   │                                     │
│   └────┬─────────────┘                                      │
│        │                                                    │
│        ▼                                                    │
│   ┌──────────────────┐    stop_reason = "end_turn"          │
│   │  CHECK STOP REASON │─────────────────────────► DONE     │
│   └────┬─────────────┘                                      │
│        │ stop_reason = "tool_use"                           │
│        ▼                                                    │
│   ┌──────────────────┐                                      │
│   │  EXTRACT TOOL CALL │  name: "Read", args: {path: ...}  │
│   └────┬─────────────┘                                      │
│        │                                                    │
│        ▼                                                    │
│   ┌──────────────────┐                                      │
│   │  EXECUTE TOOL      │  YOUR CODE runs the program        │
│   └────┬─────────────┘                                      │
│        │                                                    │
│        ▼                                                    │
│   ┌──────────────────┐                                      │
│   │  APPEND RESULT     │  ToolResultBlock → conversation    │
│   └────┬─────────────┘                                      │
│        │                                                    │
│        └──────────────► back to MODEL RESPONDS              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## stop_reason: The Decision Point

After the model responds, you check `stop_reason` to decide what happens next:

| `stop_reason` | Meaning | What You Do |
|---|---|---|
| `"end_turn"` | Model is finished. It has a final answer. | Return the result. Loop ends. |
| `"tool_use"` | Model wants to call a tool. It needs more information or wants to take an action. | Execute the tool, append the result, send it back. Loop continues. |

This is the **only branching point** in the loop. Everything else is the same: send messages, get response, check `stop_reason`.

## Example: Step by Step

Let's trace through a real agent run:

```
STEP 1: User sends prompt
  "Read auth.py and tell me what's wrong"

STEP 2: Model responds
  stop_reason: "tool_use"
  content: [ToolUseBlock(name="Read", args={file_path: "auth.py"})]
  
  → Model wants to read a file. It can't read files itself.
  → It's asking YOUR code to read the file.

STEP 3: Your code executes the Read tool
  result = readFile("auth.py")
  → result: "def authenticate(user):\n    if user == 'admin':\n        return True\n    return False"

STEP 4: You append the result
  [ToolResultBlock(tool_use_id="toolu_abc", content="def authenticate(user):...")]

STEP 5: Model responds again
  stop_reason: "end_turn"
  content: [TextBlock(text="I found a critical security bug...")]
  
  → Model has enough information. It's done.
  → Loop ends.
```

**Total loop iterations: 2** (one tool call, then final answer)

## What If There Are Multiple Tools?

The model can call multiple tools in sequence:

```
Prompt: "Find all TODO comments in the codebase"

Turn 1: Model calls Glob("*.py") → finds files
Turn 2: Model calls Read("src/app.py") → reads first file
Turn 3: Model calls Read("src/utils.py") → reads second file
Turn 4: Model calls Read("tests/test_app.py") → reads third file
Turn 5: Model generates final answer with all TODOs found

Total: 4 tool calls, 5 model responses, stop_reason changes:
  tool_use → tool_use → tool_use → tool_use → end_turn
```

The model decides how many tools to call based on what it needs. You don't control this — the model's reasoning determines the path.

## SDK vs Manual Control

| API | Loop Control | Use When |
|---|---|---|
| `query()` | **Automatic** — SDK runs the loop for you | Most cases. Simple, reliable. |
| `ClaudeSDKClient` | **Manual** — you observe each step | You need to intercept tool calls, modify behavior, or run custom logic between steps. |

With `query()`, you just see the messages stream by. With `ClaudeSDKClient`, you can:
- Observe each tool call before it executes
- Modify tool arguments
- Block certain tools
- Run custom code between turns

## The Key Insight

The agentic loop is just **repeated tool calls**. Each tool call is a computer program that runs locally or over the internet. The model decides what programs to run and in what order. Your code executes them. The loop continues until the model has enough information to give a final answer.

This is why agents are powerful: the model can reason about complex, multi-step tasks and break them down into concrete actions that your tools execute in the real world.

## Next

Learn about [the message protocol](04-message-protocol.md) — the data structures that flow through the loop.
