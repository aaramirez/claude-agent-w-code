"""
Example 01: Basic Agent (TUI)

The simplest TUI example. An interactive agent with file-reading tools.
Type anything and see the model respond with formatted, color-coded output.

Tools: Read, Glob, Grep — the model can inspect your codebase.
Debug mode is ON by default — use /debug to toggle.

Run:
    cd tutorial/03-tui
    pip install -r requirements.txt
    python examples/01-basic-agent.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent_tui import AgentTuiApp


def main():
    app = AgentTuiApp(
        allowed_tools=["Read", "Glob", "Grep"],
        permission_mode="acceptEdits",
    )
    app.run()


if __name__ == "__main__":
    main()
