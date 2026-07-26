"""
Example 07: Permissions

Fine-grained control over which tools the agent can use and when.
The can_use_tool callback is the SDK's permission gate — it runs
for any tool call that would normally prompt the user for approval.

This is more powerful than allowed_tools because it can:
- Inspect the tool arguments before allowing execution
- Make dynamic decisions based on context
- Provide custom denial messages
- Interrupt the agent entirely

Concepts introduced:
- can_use_tool — permission callback for tool execution
- PermissionResultDeny — deny a tool call with a message
- ToolPermissionContext — context about the tool call
- interrupt — halt the agent when something dangerous is attempted
"""

import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    PermissionResultDeny,
    ToolPermissionContext,
)


# ─── Permission Callback ──────────────────────────────────────────────
# This function is called for every tool that would normally prompt
# the user. Return {"behavior": "allow"} to allow, or PermissionResultDeny
# to block.

BLOCKED_PATTERNS = [
    "rm -rf",
    "sudo rm",
    "chmod 777",
    "mkfs",
    "dd if=",
    ":(){ :|:& };:",  # fork bomb
]


async def safety_check(
    tool_name: str,
    tool_input: dict,
    context: ToolPermissionContext,
):
    """
    Called for every tool that needs permission.
    
    tool_name: which tool (e.g. "Bash", "Write", "Edit")
    tool_input: the arguments the model wants to pass
    context: additional context about the call
    
    Return:
    - {"behavior": "allow"} to let it through
    - PermissionResultDeny(...) to block it
    """
    # Block dangerous bash commands
    if tool_name == "Bash":
        command = str(tool_input.get("command", ""))
        for pattern in BLOCKED_PATTERNS:
            if pattern in command:
                return PermissionResultDeny(
                    behavior="deny",
                    message=f"Blocked: command contains '{pattern}'",
                    interrupt=True,  # Stop the agent entirely
                )
    
    # Block writes to system directories
    if tool_name in ("Write", "Edit"):
        file_path = str(tool_input.get("file_path", ""))
        if file_path.startswith("/etc") or file_path.startswith("/usr"):
            return PermissionResultDeny(
                behavior="deny",
                message=f"Cannot modify system files: {file_path}",
                interrupt=False,  # Let the agent try a different approach
            )
    
    # Allow everything else
    return {"behavior": "allow"}


async def main():
    """
    Test the safety check with a prompt that tries to run dangerous commands.
    
    The agent will try to run the command, get blocked, and (hopefully)
    find a safer alternative.
    """
    options = ClaudeAgentOptions(
        allowed_tools=["Bash", "Read", "Write"],
        can_use_tool=safety_check,
    )

    async with ClaudeSDKClient(options) as client:
        await client.connect(
            prompt="Run 'ls -la' to list files, then try 'rm -rf /tmp/test' to clean up"
        )
        async for msg in client.receive_response():
            print(msg)


if __name__ == "__main__":
    asyncio.run(main())
