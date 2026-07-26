"""
Example 02: Agentic Loop Visualization (TUI)

Visualizes the agentic loop step by step. Each iteration of the loop
is numbered and color-coded so you can see exactly what happens:

  1. User sends prompt
  2. Model generates text OR requests a tool call
  3. If tool_use → execute → append result → loop back
  4. If end_turn → done

Watch the stop_reason change from "tool_use" to "end_turn" in the debug output.

Tools: Read, Glob — the model will read files in multiple steps.
Debug mode: ON (shows loop iteration details)

Run:
    cd tutorial/03-tui
    pip install -r requirements.txt
    python examples/02-agentic-loop-visual.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent_tui import AgentTuiApp


def main():
    """
    Launch the TUI with tools that force multi-step reasoning.
    """
    app = AgentTuiApp(
        allowed_tools=["Read", "Glob", "Grep"],
        permission_mode="acceptEdits",
        instructions=(
            "Try asking:\n"
            '  - "Read all Python files and summarize what each does"\n'
            '  - "Find the main entry point of this project"\n'
            '  - "List all functions defined in agent_tui.py"'
        ),
    )
    app.run()


if __name__ == "__main__":
    main()
