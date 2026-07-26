/**
 * Example 05: Bidirectional Streaming
 *
 * ClaudeSDKClient gives you more control than query(). With it, you can:
 * - Maintain a persistent session across multiple queries
 * - Observe each message as it arrives
 * - Send follow-up prompts in the same context
 *
 * This is the difference:
 * - query() = fire-and-forget, you just see messages stream by
 * - ClaudeSDKClient = interactive session, you control the conversation
 *
 * Concepts introduced:
 * - ClaudeSDKClient — the interactive client
 * - connect() — start a session with an initial prompt
 * - query() — send additional prompts in the same session
 * - receiveResponse() — async iterator over messages
 * - disconnect() — end the session
 * - Session persistence — Claude remembers everything from prior queries
 */

import { ClaudeSDKClient } from "@anthropic-ai/claude-agent-sdk";
import type { AssistantMessage } from "@anthropic-ai/claude-agent-sdk";

async function main() {
  /**
   * Start an interactive session with Claude.
   *
   * 1. Connect with an initial prompt (lists files in the directory)
   * 2. Send a follow-up (reads the main file)
   * 3. Send another follow-up (explains what it found)
   *
   * All three queries share the same context — Claude remembers everything.
   */
  const client = new ClaudeSDKClient({
    allowedTools: ["Read", "Glob", "Grep"],
    permissionMode: "acceptEdits",
  });

  try {
    // ── First query ──────────────────────────────────────────────
    console.log("=".repeat(50));
    console.log("QUERY 1: List files in the directory");
    console.log("=".repeat(50));

    await client.connect({ prompt: "What files are in the current directory? List them all." });
    for await (const msg of client.receiveResponse()) {
      if (msg.type === "assistant") {
        for (const block of msg.content) {
          if (block.type === "text") {
            console.log(`\nClaude: ${block.text}`);
          } else if (block.type === "tool_use") {
            console.log(`  → ${block.name}(${JSON.stringify(block.arguments)})`);
          }
        }
      }
    }

    // ── Second query (same session) ──────────────────────────────
    console.log("\n" + "=".repeat(50));
    console.log("QUERY 2: Read the main file");
    console.log("=".repeat(50));

    await client.query("Now read the first TypeScript file you found and explain what it does");
    for await (const msg of client.receiveResponse()) {
      if (msg.type === "assistant") {
        for (const block of msg.content) {
          if (block.type === "text") {
            console.log(`\nClaude: ${block.text}`);
          } else if (block.type === "tool_use") {
            console.log(`  → ${block.name}(${JSON.stringify(block.arguments)})`);
          }
        }
      }
    }

    // ── Third query (same session) ───────────────────────────────
    console.log("\n" + "=".repeat(50));
    console.log("QUERY 3: Summarize everything");
    console.log("=".repeat(50));

    await client.query("Based on everything you've seen, give me a brief summary of this project");
    for await (const msg of client.receiveResponse()) {
      if (msg.type === "assistant") {
        for (const block of msg.content) {
          if (block.type === "text") {
            console.log(`\nClaude: ${block.text}`);
          }
        }
      }
    }
  } finally {
    await client.disconnect();
  }
}

main();
