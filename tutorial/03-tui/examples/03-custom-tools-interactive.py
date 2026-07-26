"""
Example 03: Custom Tools Interactive (TUI)

Demonstrates custom tools in the TUI. The model can:
  - Calculate math expressions (local computation)
  - Get weather data (simulated API call)
  - Query a database (simulated)

These tools run LOCALLY on your machine — the model only generates
the request (name + arguments as JSON), your code executes it.

Watch the TUI show tool calls in yellow and results in dim white.

Run:
    cd tutorial/03-tui
    pip install -r requirements.txt
    python examples/03-custom-tools-interactive.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions

from agent_tui import AgentTuiApp


# ── Custom Tools ───────────────────────────────────────────────────────

@tool("calculate", "Evaluate a math expression. Supports +, -, *, /, **, and parentheses.", {"expression": str})
async def calculate(args):
    """Evaluate a math expression safely."""
    try:
        result = eval(args["expression"])
        return {"content": [{"type": "text", "text": str(result)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {e}"}]}


@tool("get_weather", "Get the current weather for a city. Returns temperature and conditions.", {"city": str})
async def get_weather(args):
    """Fetch weather for a city (simulated)."""
    city = args["city"]
    return {"content": [{"type": "text", "text": f"Weather in {city}: 72F (22C), sunny, humidity 45%"}]}


@tool("query_db", "Query the users database. Pass a SQL-like query string.", {"query": str})
async def query_db(args):
    """Simulated database query."""
    return {"content": [{"type": "text", "text": f"Query result for '{args['query']}': 42 users found"}]}


# ── Custom TUI App ────────────────────────────────────────────────────

class CustomToolsTuiApp(AgentTuiApp):
    """TUI app with custom tools registered via MCP."""

    def _build_options(self):
        server = create_sdk_mcp_server(
            "mytools",
            tools=[calculate, get_weather, query_db],
        )
        return ClaudeAgentOptions(
            mcp_servers={"mytools": server},
            allowed_tools=["mcp__mytools__*"],
        )


def main():
    """
    Launch the TUI with custom tools.
    """
    app = CustomToolsTuiApp(
        instructions=(
            "Try asking:\n"
            '  - "What\'s 15 * 7 + 3?"\n'
            '  - "What\'s the weather in NYC?"\n'
            '  - "How many users are in the database?"\n'
            '  - "Get the weather in London, then calculate the temperature in Celsius"'
        ),
    )
    app.run()


if __name__ == "__main__":
    main()
