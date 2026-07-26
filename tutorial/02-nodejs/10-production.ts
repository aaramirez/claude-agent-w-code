/**
 * Example 10: Production Patterns
 *
 * Real-world agents need: tracing, cost control, error handling, and
 * structured output. This example shows how to build an agent that's
 * ready for production use.
 *
 * Key production concerns:
 * - Cost control: cap spending per session
 * - Turn limits: prevent infinite loops
 * - Tracing: log every tool call for debugging
 * - Error handling: gracefully handle failures
 * - Terminal reason: know WHY the agent stopped
 *
 * Concepts introduced:
 * - maxTurns — limit the number of loop iterations
 * - maxBudgetUsd — cap spending per session
 * - terminalReason — "completed", "maxTurns", "aborted_*"
 * - Structured tracing — log every step for debugging
 */

import { query } from "@anthropic-ai/claude-agent-sdk";
import { writeFileSync } from "fs";

interface AgentTrace {
  start: string;
  prompt: string;
  turns: Array<{ blocks: Array<Record<string, any>> }>;
  result?: {
    stopReason: string | null;
    terminalReason: string | null;
    numTurns: number;
    costUsd: number | null;
    sessionId: string;
    isError: boolean;
  };
  resultText?: string | null;
  error?: string;
  errorType?: string;
  end?: string;
}

/**
 * Run an agent with full tracing and safety limits.
 *
 * Returns a trace object with:
 * - start/end timestamps
 * - every tool call made
 * - final result (stop_reason, cost, turns)
 * - any errors that occurred
 */
async function runAgent(
  prompt: string,
  maxTurns: number = 10,
  maxBudget: number = 0.50
): Promise<AgentTrace> {
  const trace: AgentTrace = {
    start: new Date().toISOString(),
    prompt,
    turns: [],
  };

  try {
    for await (const msg of query({
      prompt,
      options: {
        allowedTools: ["Read", "Edit", "Bash", "Glob", "Grep"],
        permissionMode: "acceptEdits",
        maxTurns,          // Safety: stop after N turns
        maxBudgetUsd: maxBudget, // Safety: stop after $X spent
      },
    })) {
      if (msg.type === "assistant") {
        const turn = {
          blocks: msg.content.map((block: any) => {
            if (block.type === "text") {
              return { type: "text", text: block.text };
            } else if (block.type === "tool_use") {
              // Log each tool call
              console.log(`  [TOOL] ${block.name}(${JSON.stringify(block.arguments)})`);
              return { type: "tool_use", name: block.name, args: block.arguments };
            }
            return { type: block.type };
          }),
        };
        trace.turns.push(turn);
      } else if (msg.type === "result") {
        trace.result = {
          stopReason: msg.stop_reason,
          terminalReason: msg.terminal_reason,
          numTurns: msg.num_turns,
          costUsd: msg.total_cost_usd,
          sessionId: msg.session_id,
          isError: msg.is_error,
        };
        trace.resultText = msg.result;
      }
    }
  } catch (e) {
    trace.error = String(e);
    trace.errorType = e?.constructor?.name ?? "Unknown";
  }

  trace.end = new Date().toISOString();
  return trace;
}

async function main() {
  /**
   * Run an agent with production-grade tracing.
   *
   * The agent will:
   * 1. Find and create a TODO summary (or try to)
   * 2. Every tool call is logged
   * 3. Cost is tracked
   * 4. If it hits maxTurns or maxBudget, it stops gracefully
   */
  console.log("Running agent with production tracing...\n");

  const trace = await runAgent(
    prompt: "Find all TODO comments in the TypeScript files and create a TODO.md summary",
    maxTurns: 8,
    maxBudget: 0.50,
  );

  // Save the trace
  writeFileSync("agent_trace.json", JSON.stringify(trace, null, 2));

  // Print summary
  console.log("\n" + "=".repeat(50));
  console.log("AGENT TRACE SUMMARY");
  console.log("=".repeat(50));
  console.log(`Start:          ${trace.start}`);
  console.log(`End:            ${trace.end}`);
  console.log(`Total turns:    ${trace.turns.length}`);

  if (trace.result) {
    const r = trace.result;
    console.log(`Stop reason:    ${r.stopReason}`);
    console.log(`Terminal:       ${r.terminalReason}`);
    console.log(`API turns:      ${r.numTurns}`);
    console.log(`Cost:           $${r.costUsd?.toFixed(4) ?? "N/A"}`);
    console.log(`Session:        ${r.sessionId}`);
    console.log(`Error:          ${r.isError}`);
  } else if (trace.error) {
    console.log(`ERROR:          ${trace.error}`);
  }

  console.log(`\nFull trace saved to agent_trace.json`);
}

main();
