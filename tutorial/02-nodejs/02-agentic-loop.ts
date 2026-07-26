/**
 * Example 02: The Agentic Loop in Action
 *
 * This example lets you OBSERVE the agentic loop — the repeated cycle of
 * model response → tool call → execute → result → model response → ... → done.
 *
 * We give the model access to the Read and Glob tools so it can inspect files.
 * Watch how it calls tools, gets results, and reasons about them.
 *
 * Concepts introduced:
 * - msg.type === "assistant" — the model's response
 * - content blocks: text, tool_use — what the model generates
 * - msg.type === "result" — final metadata: stop_reason, cost, num_turns
 * - stop_reason — "tool_use" means the loop continues, "end_turn" means it's done
 */

import { query } from "@anthropic-ai/claude-agent-sdk";

async function main() {
  /**
   * Ask Claude to read the README file and summarize it.
   *
   * The model will:
   * 1. Decide it needs to read the file (generates a tool_use block for "Read")
   * 2. The SDK executes the Read tool and appends the result
   * 3. The model reads the result and generates a summary (text block)
   * 4. stop_reason becomes "end_turn" — loop ends
   */
  for await (const msg of query({
    prompt: "Read the README.md in the current directory and give me a 2-sentence summary",
    options: {
      allowedTools: ["Read", "Glob"], // Model can read files and search by pattern
    },
  })) {
    if (msg.type === "assistant") {
      for (const block of msg.content) {
        if (block.type === "text") {
          // The model is talking — print its text
          console.log(`\n[TEXT] ${block.text}`);
        } else if (block.type === "tool_use") {
          // The model wants to call a tool — show what it's doing
          console.log(`\n[TOOL_USE] ${block.name}(${JSON.stringify(block.arguments)})`);
          // The SDK will execute this tool and append the result automatically.
          // You don't need to do anything here — just observe.
        }
      }
    } else if (msg.type === "result") {
      // The loop has ended — show final metadata
      console.log(`\n${"=".repeat(50)}`);
      console.log(`STOP REASON:    ${msg.stop_reason}`);
      console.log(`TERMINAL:       ${msg.terminal_reason}`);
      console.log(`NUM TURNS:      ${msg.num_turns}`);
      console.log(`COST:           $${msg.total_cost_usd?.toFixed(4) ?? "N/A"}`);
      console.log(`SESSION ID:     ${msg.session_id}`);
      console.log(`${"=".repeat(50)}`);
    }
  }
}

main();
