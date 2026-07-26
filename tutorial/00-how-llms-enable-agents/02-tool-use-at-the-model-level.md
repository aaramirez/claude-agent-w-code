# Tool Calls Are Just Computer Programs

When the model generates a tool call, it's requesting that YOUR code execute a program. That program can be anything a computer can do.

## What Is a "Tool"?

A tool is **any function or program that your code can execute**. The model doesn't run the tool — it generates a JSON description of which tool to call and with what arguments. Your code then runs the actual program.

The possibilities are unlimited:

### Local Operations
- Read, write, or delete files on your disk
- Run shell commands (`ls`, `git`, `docker`, `make`, anything)
- Execute scripts you wrote (Python, Bash, Node, anything)
- Run installed programs (compilers, formatters, linters)
- Access environment variables and configuration

### Network Operations
- Call REST APIs (Stripe, Twilio, GitHub, any web service)
- Query databases (PostgreSQL, MongoDB, Redis, SQLite)
- Send HTTP requests to any URL
- Connect to WebSocket servers
- Fetch web pages and parse HTML

### Local Programs That Use the Internet
- A Python script that calls OpenAI's API
- A Node app that streams from a video service
- A CLI tool that uploads files to S3
- A script that scrapes a website
- Any program that makes network requests

### Hardware and External Systems
- Control GPIO pins on a Raspberry Pi
- Send commands over serial ports
- Interact with USB devices
- Control robots, drones, or industrial equipment
- Send emails, SMS, or Slack messages

### Complex Workflows
- Run a multi-step build process
- Execute a database migration
- Deploy code to a server
- Run a test suite and collect results
- Generate a report from multiple data sources

## How It Works: The Request-Response Cycle

```
1. Model generates: "I need to read auth.py"
   
   ToolUseBlock {
     name: "Read",
     arguments: { "file_path": "auth.py" }
   }

2. YOUR CODE executes the Read tool:
   
   // This is YOUR function running on YOUR machine
   const contents = await readFile("auth.py");
   
3. YOUR CODE sends the result back to the model:
   
   ToolResultBlock {
     tool_use_id: "toolu_abc123",
     content: "def authenticate(user):\n    ..."
   }

4. Model sees the result and decides what to do next:
   
   "I see a bug on line 3. Let me fix it..."
```

The model generates the **request**. Your code does the **work**. The model gets the **result** and reasons about it.

## Why This Design Is Powerful

The model can reason about what to do, but it can't do it alone. By giving it tools, you give it the ability to affect the real world. The model becomes a **general-purpose reasoning engine** that can:

- Decide what information it needs (and request it via tools)
- Decide what action to take (and request it via tools)
- Process the results and decide what to do next
- Repeat until the task is complete

This is the foundation of AI agents: a model that thinks + tools that act = an autonomous system.

## The Model's Role vs Your Role

| The Model Decides | Your Code Executes |
|---|---|
| "I need to read a file" | `readFile("auth.py")` |
| "I need to search for patterns" | `grep("TODO", "*.py")` |
| "I need to run a command" | `exec("python -m pytest")` |
| "I need to call an API" | `fetch("https://api.example.com")` |
| "I need to write a file" | `writeFile("output.txt", data)` |

The model is the **decision-maker**. Your tools are the **executors**. The agentic loop connects them.

## Next

Learn about [the agentic loop](03-the-agentic-loop-explained.md) — how the model and tools work together in a repeating cycle until the task is done.
