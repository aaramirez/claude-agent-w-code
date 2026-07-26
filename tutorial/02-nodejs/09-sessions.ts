/**
 * Example 09: Sessions
 *
 * Sessions let you save and resume the agent's context across multiple
 * queries. Claude remembers everything: files read, analysis done,
 * conversation history, and tool results.
 *
 * Why use sessions?
 * - Long-running tasks: break a big task into smaller steps
 * - Interactive workflows: user reviews between steps
 * - Context persistence: Claude remembers what it learned earlier
 * - Forking: explore different approaches from the same starting point
 *
 * Concepts introduced:
 * - sessionId — unique identifier for a conversation
 * - SystemMessage with subtype="init" — contains the sessionId
 * - resume — continue an existing session
 * - forkSession — branch from an existing session
 */

import { query } from "@anthropic-ai/claude-agent-sdk";

async function main() {
  /**
   * Two-step workflow:
   *
   * Step 1: Ask Claude to analyze auth.py and remember the issues
   *         Capture the sessionId from the init message
   *
   * Step 2: Resume the session and ask Claude to fix the issues
   *         Claude remembers everything from step 1
   *
   * Without sessions, step 2 would have no context — Claude wouldn't
   * know what issues were found. With sessions, it remembers everything.
   */
  let sessionId: string | undefined;

  // ── Step 1: Analyze the code ─────────────────────────────────────
  console.log("=".repeat(50));
  console.log("STEP 1: Analyze auth files");
  console.log("=".repeat(50));

  try {
    for await (const msg of query({
      prompt:
        "Read the auth-related TypeScript files in this directory. " +
        "Identify all security issues and best practice violations. " +
        "Remember what you find — I'll ask you to fix them next.",
      options: {
        allowedTools: ["Read", "Glob", "Grep"],
      },
    })) {
      // Capture the sessionId from the init message
      if (msg.type === "system" && msg.subtype === "init") {
        sessionId = msg.session_id;
        console.log(`Session started: ${sessionId}`);
      }

      if (msg.type === "result") {
        console.log(`\nAnalysis complete. ${msg.num_turns} turns, $${msg.total_cost_usd?.toFixed(4) ?? "N/A"}`);
      }
    }
  } catch (error) {
    console.error(`Session ended with error: ${error}`);
  }

  if (!sessionId) {
    console.error("ERROR: No sessionId captured");
    return;
  }

  // ── Step 2: Fix the issues (resume session) ─────────────────────
  console.log("\n" + "=".repeat(50));
  console.log("STEP 2: Fix the issues (resuming session)");
  console.log("=".repeat(50));

  for await (const msg of query({
    prompt: "Now fix all the security issues you found. Make the minimal necessary changes.",
    options: {
      resume: sessionId,              // Resume the previous session
      allowedTools: ["Read", "Edit"], // Can read and edit files
    },
  })) {
    if (msg.type === "result") {
      console.log(`\nFix complete. ${msg.num_turns} turns, $${msg.total_cost_usd?.toFixed(4) ?? "N/A"}`);
      console.log(`Stop reason: ${msg.stop_reason}`);
    }
  }
}

main();
