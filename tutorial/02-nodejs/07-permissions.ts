/**
 * Example 07: Permissions
 *
 * Fine-grained control over which tools the agent can use and when.
 * The canUseTool callback is the SDK's permission gate — it runs
 * for any tool call that would normally prompt the user for approval.
 *
 * This is more powerful than allowedTools because it can:
 * - Inspect the tool arguments before allowing execution
 * - Make dynamic decisions based on context
 * - Provide custom denial messages
 * - Interrupt the agent entirely
 *
 * Concepts introduced:
 * - canUseTool — permission callback for tool execution
 * - PermissionResultDeny — deny a tool call with a message
 * - interrupt — halt the agent when something dangerous is attempted
 */

import { ClaudeSDKClient } from "@anthropic-ai/claude-agent-sdk";

const BLOCKED_PATTERNS = [
  "rm -rf",
  "sudo rm",
  "chmod 777",
  "mkfs",
  "dd if=",
  ":(){ :|:& };:", // fork bomb
];

/**
 * Called for every tool that needs permission.
 *
 * toolName: which tool (e.g. "Bash", "Write", "Edit")
 * toolInput: the arguments the model wants to pass
 * context: additional context about the call
 *
 * Return:
 * - { behavior: "allow" } to let it through
 * - { behavior: "deny", message: "...", interrupt: true/false } to block it
 */
async function safetyCheck(
  toolName: string,
  toolInput: any,
  _context: any
): Promise<{ behavior: "allow" } | { behavior: "deny"; message: string; interrupt: boolean }> {
  // Block dangerous bash commands
  if (toolName === "Bash") {
    const command = String(toolInput?.command ?? "");
    for (const pattern of BLOCKED_PATTERNS) {
      if (command.includes(pattern)) {
        return {
          behavior: "deny",
          message: `Blocked: command contains '${pattern}'`,
          interrupt: true, // Stop the agent entirely
        };
      }
    }
  }

  // Block writes to system directories
  if (toolName === "Write" || toolName === "Edit") {
    const filePath = String(toolInput?.file_path ?? "");
    if (filePath.startsWith("/etc") || filePath.startsWith("/usr")) {
      return {
        behavior: "deny",
        message: `Cannot modify system files: ${filePath}`,
        interrupt: false, // Let the agent try a different approach
      };
    }
  }

  // Allow everything else
  return { behavior: "allow" };
}

async function main() {
  /**
   * Test the safety check with a prompt that tries to run dangerous commands.
   *
   * The agent will try to run the command, get blocked, and (hopefully)
   * find a safer alternative.
   */
  const client = new ClaudeSDKClient({
    allowedTools: ["Bash", "Read", "Write"],
    canUseTool: safetyCheck,
  });

  try {
    await client.connect({
      prompt: "Run 'ls -la' to list files, then try 'rm -rf /tmp/test' to clean up",
    });
    for await (const msg of client.receiveResponse()) {
      console.log(msg);
    }
  } finally {
    await client.disconnect();
  }
}

main();
