"""
Example 10: Production Patterns

Real-world agents need: tracing, cost control, error handling, and
structured output. This example shows how to build an agent that's
ready for production use.

Key production concerns:
- Cost control: cap spending per session
- Turn limits: prevent infinite loops
- Tracing: log every tool call for debugging
- Error handling: gracefully handle failures
- Terminal reason: know WHY the agent stopped

Concepts introduced:
- max_turns — limit the number of loop iterations
- max_budget_usd — cap spending per session
- terminal_reason — "completed", "max_turns", "aborted_*"
- Structured tracing — log every step for debugging
"""

import asyncio
import json
from datetime import datetime
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)


async def run_agent(prompt: str, max_turns: int = 10, max_budget: float = 0.50) -> dict:
    """
    Run an agent with full tracing and safety limits.
    
    Returns a trace dict with:
    - start/end timestamps
    - every tool call made
    - final result (stop_reason, cost, turns)
    - any errors that occurred
    """
    trace = {
        "start": datetime.now().isoformat(),
        "prompt": prompt,
        "turns": [],
    }

    try:
        async for msg in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                allowed_tools=["Read", "Edit", "Bash", "Glob", "Grep"],
                permission_mode="acceptEdits",
                max_turns=max_turns,           # Safety: stop after N turns
                max_budget_usd=max_budget,     # Safety: stop after $X spent
            ),
        ):
            if isinstance(msg, AssistantMessage):
                turn = {"blocks": []}
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        turn["blocks"].append({
                            "type": "text",
                            "text": block.text,
                        })
                    elif isinstance(block, ToolUseBlock):
                        turn["blocks"].append({
                            "type": "tool_use",
                            "name": block.name,
                            "args": block.arguments,
                        })
                        # Log each tool call
                        print(f"  [TOOL] {block.name}({block.arguments})")
                trace["turns"].append(turn)

            elif isinstance(msg, ResultMessage):
                trace["result"] = {
                    "stop_reason": msg.stop_reason,
                    "terminal_reason": msg.terminal_reason,
                    "num_turns": msg.num_turns,
                    "cost_usd": msg.total_cost_usd,
                    "session_id": msg.session_id,
                    "is_error": msg.is_error,
                }
                trace["result_text"] = msg.result

    except Exception as e:
        trace["error"] = str(e)
        trace["error_type"] = type(e).__name__

    trace["end"] = datetime.now().isoformat()
    return trace


async def main():
    """
    Run an agent with production-grade tracing.
    
    The agent will:
    1. Find and fix a bug (or try to)
    2. Every tool call is logged
    3. Cost is tracked
    4. If it hits max_turns or max_budget, it stops gracefully
    """
    print("Running agent with production tracing...\n")

    trace = await run_agent(
        prompt="Find all TODO comments in the Python files and create a TODO.md summary",
        max_turns=8,
        max_budget=0.50,
    )

    # Save the trace
    with open("agent_trace.json", "w") as f:
        json.dump(trace, f, indent=2, default=str)

    # Print summary
    print("\n" + "=" * 50)
    print("AGENT TRACE SUMMARY")
    print("=" * 50)
    print(f"Start:          {trace['start']}")
    print(f"End:            {trace['end']}")
    print(f"Total turns:    {len(trace['turns'])}")

    if "result" in trace:
        r = trace["result"]
        print(f"Stop reason:    {r['stop_reason']}")
        print(f"Terminal:       {r['terminal_reason']}")
        print(f"API turns:      {r['num_turns']}")
        print(f"Cost:           ${r['cost_usd']:.4f}" if r['cost_usd'] else "Cost: N/A")
        print(f"Session:        {r['session_id']}")
        print(f"Error:          {r['is_error']}")
    elif "error" in trace:
        print(f"ERROR:          {trace['error']}")

    print(f"\nFull trace saved to agent_trace.json")


if __name__ == "__main__":
    asyncio.run(main())
