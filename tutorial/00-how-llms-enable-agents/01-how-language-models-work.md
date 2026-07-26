# How Language Models Work

Before we build agents, you need to understand what the model actually does under the hood. This is not about neural network math — it's about understanding the interface so you can use it effectively.

## The Core Idea: Token Prediction

A language model is, at its simplest, a **next-token predictor**. You give it a sequence of tokens (words or parts of words), and it predicts what comes next.

```
Input:  "The capital of France is"
Output: " Paris"     (high probability)
        " Lyon"      (lower probability)
        " a beautiful" (even lower)
```

The model doesn't "know" facts the way a database does. It has learned statistical patterns from billions of examples. When it generates text, it's sampling from those learned patterns, one token at a time.

## The Context Window

The model sees a **window** of tokens — everything in the current conversation. This is called the **context window**. It includes:

1. **System prompt** — instructions you give the model (hidden from the user)
2. **Conversation history** — every message exchanged so far
3. **Current input** — what the user just said

```
┌─────────────────────────────────────┐
│  System prompt: "You are a helpful  │
│  coding assistant..."               │
├─────────────────────────────────────┤
│  User: "Read auth.py and fix bugs"  │
├─────────────────────────────────────┤
│  Assistant: [calls Read tool]       │
├─────────────────────────────────────┤
│  Tool result: "def auth(): ..."     │
├─────────────────────────────────────┤
│  Assistant: "I found a bug..."      │
├─────────────────────────────────────┤
│  User: "Fix it"                     │
└─────────────────────────────────────┘
         ↑ This is the context window
```

Everything the model has seen in this conversation influences its next response. This is why agents work — the model remembers what tools it called and what results it got.

## Why This Matters for Agents

When you send a prompt to the model, it doesn't "run" your code. It generates text. But that text can be **structured** — we can design the model's output format so that:

- Plain text → the model is talking to the user
- Structured JSON → the model is requesting a tool call

The model learned to generate structured output because we trained it with examples of tool use. The model doesn't "execute" tools — it generates a description of what tool to call with what arguments, and then YOUR code runs that tool.

## What the Model Does NOT Do

- ❌ It does not execute code
- ❌ It does not access the internet directly
- ❌ It does not read files on your computer
- ❌ It does not run shell commands

## What the Model DOES Do

- ✅ It generates text (one token at a time)
- ✅ That text can be structured (tool call requests)
- ✅ It sees the results of tools you execute
- ✅ It decides what to do next based on those results

This separation is important: **the model is the brain, your tools are the hands.** The model thinks, your code acts.

## Next

Now that you understand what the model does, learn about [tool calls](02-tool-use-at-the-model-level.md) — how the model requests actions and how you execute them.
