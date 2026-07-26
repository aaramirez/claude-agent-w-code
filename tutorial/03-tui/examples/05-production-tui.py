"""
Example 05: Production Patterns (TUI)

Production-grade agent with safety limits, cost tracking, and error handling.
The TUI shows real-time cost and turn tracking in the status bar.

Features demonstrated:
  - max_turns: limit loop iterations (prevents infinite loops)
  - max_budget_usd: cap spending per session
  - Error handling: graceful failure recovery
  - Terminal reason: know WHY the agent stopped
  - Debug mode: full visibility into SDK messages

Run:
    cd tutorial/03-tui
    pip install -r requirements.txt
    python examples/05-production-tui.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent_tui import AgentTuiApp


def main():
    """
    Launch a production-configured TUI agent.

    Safety limits:
      - max_turns=10: stops after 10 loop iterations
      - max_budget_usd=0.50: stops after $0.50 spent
      - Tools: Read, Edit, Bash, Glob, Grep (full access)

    Try asking:
      - "Find all TODO comments in the Python files"
      - "Read agent_tui.py and explain its architecture"
      - "Create a file called test.txt with hello world"
    """
    app = AgentTuiApp(
        allowed_tools=["Read", "Edit", "Bash", "Glob", "Grep"],
        permission_mode="acceptEdits",
        max_turns=10,
        max_budget_usd=0.50,
    )
    app.run()


if __name__ == "__main__":
    main()
