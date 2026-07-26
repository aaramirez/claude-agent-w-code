"""
Example 04: Custom Tools

You can create your own tools — any Python function that the model can call.
A "tool" is just a function: it can do anything a computer can do.

This example creates two custom tools:
1. calculate — evaluate a math expression (local computation)
2. get_weather — fetch weather data (simulated API call)

The @tool decorator registers your function with a name, description, and
argument schema. The model uses the description to decide WHEN to call it.

Concepts introduced:
- @tool decorator — register a Python function as a tool
- create_sdk_mcp_server() — host tools via MCP (Model Context Protocol)
- MCP tool naming — "mcp__<server>__<tool>" convention
- Tool as a function — it can call APIs, query databases, run commands, anything
"""

import asyncio
from claude_agent_sdk import tool, create_sdk_mcp_server, query, ClaudeAgentOptions, AssistantMessage, TextBlock, ToolUseBlock


# ─── Tool 1: Calculate ───────────────────────────────────────────────
# This tool evaluates a math expression. It runs LOCALLY on your machine.
# In real use, this could be any function: database query, API call, etc.

@tool("calculate", "Evaluate a math expression. Supports +, -, *, /, **, and parentheses.", {"expression": str})
async def calculate(args):
    """Evaluate a math expression safely."""
    try:
        # In production, use a proper math parser instead of eval()
        result = eval(args["expression"])
        return {"content": [{"type": "text", "text": str(result)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {e}"}]}


# ─── Tool 2: Get Weather ─────────────────────────────────────────────
# This tool simulates an API call. In real use, this could call
# weather.com, OpenWeatherMap, or any HTTP endpoint.

@tool("get_weather", "Get the current weather for a city. Returns temperature and conditions.", {"city": str})
async def get_weather(args):
    """Fetch weather for a city. This is simulated — replace with a real API call."""
    city = args["city"]
    # Simulated response — in production, call a real weather API:
    # async with httpx.AsyncClient() as client:
    #     resp = await client.get(f"https://api.openweathermap.org/...?q={city}")
    #     return {"content": [{"type": "text", "text": resp.json()["weather"]}]}
    return {"content": [{"type": "text", "text": f"Weather in {city}: 72°F (22°C), sunny, humidity 45%"}]}


# ─── Tool 3: Database Query (simulated) ──────────────────────────────
# This tool queries a database. In real use, connect to PostgreSQL,
# MongoDB, SQLite, Redis, or any data store.

@tool("query_db", "Query the users database. Pass a SQL-like query string.", {"query": str})
async def query_db(args):
    """Simulated database query. Replace with real DB connection."""
    query_str = args["query"]
    # Simulated — in production:
    # async with asyncpg.connect("postgresql://...") as conn:
    #     rows = await conn.fetch(query_str)
    #     return {"content": [{"type": "text", "text": str(rows)}]}
    return {"content": [{"type": "text", "text": f"Query result for '{query_str}': 42 users found"}]}


async def main():
    """
    Create a server with all three tools and let the model use them.
    
    The model sees the tool descriptions and decides which to call:
    - "What's 15 * 7 + 3?" → calls calculate
    - "What's the weather in NYC?" → calls get_weather
    - "How many users do we have?" → calls query_db
    
    It can also chain them: "Get the weather in London, then calculate
    the temperature in Celsius" → calls get_weather, then calculate.
    """
    # Create an MCP server hosting our tools
    server = create_sdk_mcp_server("mytools", tools=[calculate, get_weather, query_db])

    async for msg in query(
        prompt="What's 15 * 7 + 3? Also, what's the weather in NYC? And how many users are in the database?",
        options=ClaudeAgentOptions(
            mcp_servers={"mytools": server},          # Register our tool server
            allowed_tools=["mcp__mytools__*"],        # Allow all tools from our server
        ),
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(f"\n{block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"\n  → Tool: {block.name}({block.arguments})")


if __name__ == "__main__":
    asyncio.run(main())
