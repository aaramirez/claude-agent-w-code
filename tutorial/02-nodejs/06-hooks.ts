/**
 * Example 06: Lifecycle Hooks
 *
 * Hooks let you intercept the agent at specific points in its execution.
 * Use them for logging, validation, security policies, or custom behavior.
 *
 * Available hook events:
 * - PreToolUse     — fires BEFORE a tool executes (can block or modify)
 * - PostToolUse    — fires AFTER a tool executes (can log or validate)
 * - Stop           — fires when the agent loop ends
 * - SessionStart   — fires when a session begins
 * - SessionEnd     — fires when a session ends
 * - UserPromptSubmit — fires when the user submits a prompt
 *
 * This example logs every file modification to an audit trail.
 *
 * Concepts introduced:
 * - hookMatcher — matches tool names with regex and attaches callbacks
 * - Hook callback signature — (input, toolUseId, context) => Record
 * - PreToolUse vs PostToolUse — before vs after execution
 */

import { query, hookMatcher } from "@anthropic-ai/claude-agent-sdk";
import { appendFileSync, writeFileSync } from "fs";

// ─── Hook: Log every file change ─────────────────────────────────────
// This fires AFTER Write or Edit tools execute.
// It logs the file path and timestamp to an audit file.

async function logFileChange(input: any, _toolUseId: string, _context: any): Promise<Record<string, unknown>> {
  /**
   * PostToolUse hook: runs after Write or Edit completes.
   *
   * input contains:
   *   - tool_name: string — which tool was called
   *   - tool_input: Record — the arguments the model passed
   *   - tool_output: Record — the result that was returned
   *
   * Return an empty record to continue normally, or return a record with
   * an "error" key to fail the tool call.
   */
  const toolInput = input?.tool_input ?? {};
  const filePath = toolInput.file_path ?? "unknown";
  const toolName = input?.tool_name ?? "unknown";

  const logEntry = `[${new Date().toISOString()}] ${toolName}: ${filePath}\n`;
  appendFileSync("audit.log", logEntry);

  console.log(`  [AUDIT] ${toolName}: ${filePath}`);
  return {};
}

// ─── Hook: Block dangerous Bash commands ──────────────────────────────
// This fires BEFORE Bash executes.
// Return {"error": "..."} to block the tool call.

async function blockDangerousCommands(input: any, _toolUseId: string, _context: any): Promise<Record<string, unknown>> {
  /**
   * PreToolUse hook: runs BEFORE Bash executes.
   *
   * Return {"error": "message"} to block the command.
   * Return {} to allow it.
   */
  const toolInput = input?.tool_input ?? {};
  const command = toolInput.command ?? "";

  const dangerous = ["rm -rf /", "sudo rm", "chmod 777 /", ":(){ :|:& };:"];

  for (const pattern of dangerous) {
    if (command.includes(pattern)) {
      console.log(`  [BLOCKED] Dangerous command: ${command}`);
      return { error: `Command blocked by safety policy: '${pattern}' detected` };
    }
  }

  return {};
}

async function main() {
  /**
   * Create an agent with hooks that:
   * 1. Log every file modification to audit.log
   * 2. Block dangerous shell commands
   *
   * The model will try to create a file — watch the hook fire.
   */
  for await (const msg of query({
    prompt: "Create a file called hello.ts that prints 'Hello, World!'",
    options: {
      allowedTools: ["Read", "Write", "Edit", "Bash"],
      permissionMode: "acceptEdits",
      hooks: {
        // PostToolUse: fires AFTER Write or Edit
        PostToolUse: [
          hookMatcher("Write|Edit", [logFileChange]), // Regex matching tool names
        ],
        // PreToolUse: fires BEFORE Bash
        PreToolUse: [
          hookMatcher("Bash", [blockDangerousCommands]),
        ],
      },
    },
  })) {
    if ("result" in msg) {
      console.log(`\nResult: ${msg.result}`);
    }
  }
}

main();
