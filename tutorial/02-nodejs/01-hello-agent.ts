/**
 * Example 01: Hello Agent
 *
 * The simplest possible agent. Sends a prompt to Claude and prints the response.
 *
 * No tools are used — the model just generates text.
 *
 * Concepts introduced:
 * - query() — the main entry point for sending prompts
 * - allowedTools — which tools the model can use (empty = none)
 * - for await — processing streamed messages
 */

import { query } from "@anthropic-ai/claude-agent-sdk";

/**
 * Send a simple prompt and print every message the model sends back.
 *
 * With no tools allowed, the model can only generate text.
 * It cannot read files, run commands, or access the internet.
 */
async function main() {
  for await (const msg of query({
    prompt: "Say hello in 3 languages with a brief translation",
    options: {
      allowedTools: [], // No tools — text-only response
    },
  })) {
    // Messages stream in as the model generates them.
    // With no tools, you'll get assistant messages with text blocks.
    console.log(msg);
  }
}

main();
