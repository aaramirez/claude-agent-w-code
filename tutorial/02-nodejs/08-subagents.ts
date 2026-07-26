/**
 * Example 08: Subagents
 *
 * Subagents are specialized workers that the main agent delegates tasks to.
 * Each subagent has its own tools and system prompt — they're isolated
 * from each other and from the main agent.
 *
 * Why use subagents?
 * - Separation of concerns: one agent for code review, another for docs
 * - Tool isolation: security auditor can't write files, docs writer can't run bash
 * - Parallel execution: multiple subagents can work on different parts
 * - Focused context: each subagent only sees what it needs
 *
 * Concepts introduced:
 * - agents option — define subagents with description, prompt, and tools
 * - Agent tool — the main agent invokes subagents via the "Agent" tool
 * - parent_tool_use_id — track which messages belong to which subagent
 * - Tool isolation — each subagent has its own allowed tools
 */

import { query } from "@anthropic-ai/claude-agent-sdk";
import type { AssistantMessage } from "@anthropic-ai/claude-agent-sdk";

async function main() {
  /**
   * Create a main agent that delegates to two specialized subagents:
   *
   * 1. security-auditor — reads code and identifies security issues
   *    Tools: Read, Glob, Grep (read-only, can't modify anything)
   *
   * 2. docs-writer — writes documentation based on findings
   *    Tools: Read, Write (can write docs, can't run commands)
   *
   * The main agent orchestrates: it tells the security-auditor what to
   * review, then tells the docs-writer to document the findings.
   */
  for await (const msg of query({
    prompt:
      "First, use the security-auditor agent to check for " +
      "security vulnerabilities in the TypeScript files. " +
      "Then, use the docs-writer agent to create a SECURITY.md " +
      "file documenting the findings.",
    options: {
      // Main agent can read files and invoke subagents
      allowedTools: ["Read", "Glob", "Grep", "Agent"],
      agents: {
        "security-auditor": {
          description: "Expert security auditor for code review. Analyzes code for vulnerabilities.",
          prompt:
            "You are a security expert. Analyze the provided code for: " +
            "SQL injection, XSS, authentication flaws, insecure defaults, " +
            "exposed secrets, and other security issues. " +
            "Report each finding with severity (critical/high/medium/low).",
          tools: ["Read", "Glob", "Grep"], // Read-only — can't modify files
        },
        "docs-writer": {
          description: "Technical documentation writer. Creates clear, structured documentation.",
          prompt:
            "You are a technical writer. Create clear, well-structured " +
            "documentation. Use markdown formatting. " +
            "Include severity levels and remediation recommendations.",
          tools: ["Read", "Write"], // Can read and write docs
        },
      },
    },
  })) {
    if (msg.type === "assistant") {
      for (const block of msg.content) {
        if (block.type === "text") {
          process.stdout.write(block.text);
        } else if (block.type === "tool_use") {
          // Show which tool (or subagent) is being invoked
          console.log(`\n  → ${block.name}(${JSON.stringify(block.arguments)})`);
        }
      }
    } else if (msg.type === "result") {
      console.log(`\n\nDone. Result: ${msg.result}`);
    }
  }
}

main();
