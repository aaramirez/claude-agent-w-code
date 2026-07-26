/**
 * Example 03: Built-in Tools
 *
 * The Claude Agent SDK comes with built-in tools that the model can use.
 * These tools let the model interact with your filesystem and run commands.
 *
 * Available built-in tools:
 * - Read     — read any file in the working directory
 * - Write    — create new files
 * - Edit     — make precise edits to existing files
 * - Bash     — run terminal commands, scripts, git operations
 * - Glob     — find files by pattern (e.g. "**/*.py", "src/**/*.ts")
 * - Grep     — search file contents with regex
 * - WebSearch — search the web for current information
 * - WebFetch — fetch and parse web page content
 *
 * This example uses Glob + Read + Bash together — a common combination
 * for code analysis tasks.
 *
 * Concepts introduced:
 * - allowedTools — which tools the model can use
 * - permissionMode — "acceptEdits" auto-approves file modifications
 * - Tool combination — the model chains multiple tools in one task
 */

import { query } from "@anthropic-ai/claude-agent-sdk";

async function main() {
  /**
   * Ask Claude to find all TypeScript files and count lines in each.
   *
   * The model will likely:
   * 1. Use Glob to find *.ts files
   * 2. Use Read to read each file (or Bash with wc -l)
   * 3. Summarize the results
   *
   * Watch how it chains multiple tool calls — each one gives it more
   * information to work with.
   */
  for await (const msg of query({
    prompt: "Find all TypeScript files in the current directory and tell me how many lines each has",
    options: {
      allowedTools: ["Glob", "Read", "Bash"],
      permissionMode: "acceptEdits", // Auto-approve file operations
    },
  })) {
    if (msg.type === "assistant") {
      for (const block of msg.content) {
        if (block.type === "text") {
          process.stdout.write(block.text);
        } else if (block.type === "tool_use") {
          // Show each tool call as it happens
          console.log(`\n  → ${block.name}(${JSON.stringify(block.arguments)})`);
        }
      }
    }
  }
}

main();
