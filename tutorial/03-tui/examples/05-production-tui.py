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
    """
    app = AgentTuiApp(
        allowed_tools=["Read", "Edit", "Bash", "Glob", "Grep"],
        permission_mode="acceptEdits",
        max_turns=10,
        max_budget_usd=0.50,
        instructions=(
            "Try asking:\n"
            '  - "Find all TODO comments in the Python files"\n'
            '  - "Read agent_tui.py and explain its architecture"\n'
            '  - "Create a file called test.txt with hello world"'
        ),
    )
    app.run()


if __name__ == "__main__":
    main()
