"""
Example 11: External MCP Servers

MCP (Model Context Protocol) lets you connect any external tool server
to your agent — local or remote. The model can then use those tools
just like built-in ones.

This example connects to the Playwright MCP server for browser automation.
The model can open web pages, click buttons, fill forms, and scrape content.

Other popular MCP servers:
- Playwright — browser automation
- PostgreSQL — database queries
- GitHub — repository operations
- Slack — messaging
- Sentry — error monitoring

Concepts introduced:
- MCP server configuration — command-based (local) or URL-based (remote)
- Tool naming — "mcp__<server>__<tool>" convention
- Wildcard permissions — "mcp__playwright__*" allows all tools from a server
- Local vs remote — tools can run on your machine or across the network
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock, ToolUseBlock


async def main():
    """
    Connect to Playwright MCP server and let Claude automate a browser.
    
    The Playwright server runs locally (spawned by npx) and provides
    tools like:
    - mcp__playwright__browser_navigate — open a URL
    - mcp__playwright__browser_click — click an element
    - mcp__playwright__browser_snapshot — take a page snapshot
    
    The model sees these tools and decides how to accomplish the task.
    """
    async for msg in query(
        prompt=(
            "Open https://example.com and tell me what the main heading says. "
            "Then navigate to https://httpbin.org/get and show me the response headers."
        ),
        options=ClaudeAgentOptions(
            mcp_servers={
                "playwright": {
                    "command": "npx",
                    "args": ["@playwright/mcp@latest"],
                    # This runs the MCP server locally as a child process.
                    # For remote servers, use:
                    # "url": "https://mcp.example.com/mcp",
                }
            },
            allowed_tools=[
                "mcp__playwright__*",  # Allow ALL tools from playwright server
            ],
        ),
    ):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(block.text, end="", flush=True)
                elif isinstance(block, ToolUseBlock):
                    print(f"\n  → {block.name}({block.arguments})", flush=True)

    # ── Remote MCP example (commented out) ───────────────────────────
    # To connect to a remote MCP server instead of a local one:
    #
    # async for msg in query(
    #     prompt="Search for React hooks documentation",
    #     options=ClaudeAgentOptions(
    #         mcp_servers={
    #             "context7": {
    #                 "type": "remote",
    #                 "url": "https://mcp.context7.com/mcp",
    #                 # For authenticated servers:
    #                 # "headers": {"Authorization": "Bearer YOUR_KEY"}
    #             }
    #         },
    #         allowed_tools=["mcp__context7__*"],
    #     ),
    # ):
    #     print(msg)


if __name__ == "__main__":
    asyncio.run(main())
