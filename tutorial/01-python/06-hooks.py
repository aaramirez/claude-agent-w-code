"""
Example 06: Lifecycle Hooks

Hooks let you intercept the agent at specific points in its execution.
Use them for logging, validation, security policies, or custom behavior.

Available hook events:
- PreToolUse     — fires BEFORE a tool executes (can block or modify)
- PostToolUse    — fires AFTER a tool executes (can log or validate)
- Stop           — fires when the agent loop ends
- SessionStart   — fires when a session begins
- SessionEnd     — fires when a session ends
- UserPromptSubmit — fires when the user submits a prompt

This example logs every file modification to an audit trail.

Concepts introduced:
- HookMatcher — matches tool names with regex and attaches callbacks
- Hook callback signature — (input_data, tool_use_id, context) -> dict
- PreToolUse vs PostToolUse — before vs after execution
"""

import asyncio
from datetime import datetime
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher


# ─── Hook: Log every file change ─────────────────────────────────────
# This fires AFTER Write or Edit tools execute.
# It logs the file path and timestamp to an audit file.

async def log_file_change(input_data: dict, tool_use_id: str, context) -> dict:
    """
    PostToolUse hook: runs after Write or Edit completes.
    
    input_data contains:
      - tool_name: str — which tool was called
      - tool_input: dict — the arguments the model passed
      - tool_output: dict — the result that was returned
    
    Return an empty dict to continue normally, or return a dict with
    an "error" key to fail the tool call.
    """
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "unknown")
    tool_name = input_data.get("tool_name", "unknown")
    
    log_entry = f"[{datetime.now().isoformat()}] {tool_name}: {file_path}\n"
    
    with open("audit.log", "a") as f:
        f.write(log_entry)
    
    print(f"  [AUDIT] {tool_name}: {file_path}")
    return {}


# ─── Hook: Block dangerous Bash commands ──────────────────────────────
# This fires BEFORE Bash executes.
# Return {"error": "..."} to block the tool call.

async def block_dangerous_commands(input_data: dict, tool_use_id: str, context) -> dict:
    """
    PreToolUse hook: runs BEFORE Bash executes.
    
    Return {"error": "message"} to block the command.
    Return {} to allow it.
    """
    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")
    
    dangerous = ["rm -rf /", "sudo rm", "chmod 777 /", ":(){ :|:& };:"]
    
    for pattern in dangerous:
        if pattern in command:
            print(f"  [BLOCKED] Dangerous command: {command}")
            return {"error": f"Command blocked by safety policy: '{pattern}' detected"}
    
    return {}


async def main():
    """
    Create an agent with hooks that:
    1. Log every file modification to audit.log
    2. Block dangerous shell commands
    
    The model will try to create a file — watch the hook fire.
    """
    async for msg in query(
        prompt="Create a file called hello.py that prints 'Hello, World!'",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Write", "Edit", "Bash"],
            permission_mode="acceptEdits",
            hooks={
                # PostToolUse: fires AFTER Write or Edit
                "PostToolUse": [
                    HookMatcher(
                        matcher="Write|Edit",  # Regex matching tool names
                        hooks=[log_file_change]
                    )
                ],
                # PreToolUse: fires BEFORE Bash
                "PreToolUse": [
                    HookMatcher(
                        matcher="Bash",
                        hooks=[block_dangerous_commands]
                    )
                ],
            },
        ),
    ):
        if hasattr(msg, "result"):
            print(f"\nResult: {msg.result}")


if __name__ == "__main__":
    asyncio.run(main())
