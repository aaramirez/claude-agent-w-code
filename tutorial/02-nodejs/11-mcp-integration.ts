/**
 * Example 11: External MCP Servers
 *
 * MCP (Model Context Protocol) lets you connect any external tool server
 * to your agent — local or remote. The model can then use those tools
 * just like built-in ones.
 *
 * This example connects to the Playwright MCP server for browser automation.
 * The model can open web pages, click buttons, fill forms, and scrape content.
 *
 * Other popular MCP servers:
 * - Playwright — browser automation
 * - PostgreSQL — database queries
 * - GitHub — repository operations
 * - Slack — messaging
 * - Sentry — error monitoring
 *
 * Concepts introduced:
 * - MCP server configuration — command-based (local) or URL-based (remote)
 * - Tool naming — "mcp__<server>__<tool>" convention
 * - Wildcard permissions — "mcp__playwright__*" allows all tools from a server
 * - Local vs remote — tools can run on your machine or across the network
 */

import { query } from "@anthropic-ai/claude-agent-sdk";
import type { AssistantMessage } from "@anthropic-ai/claude-agent-sdk";

async function main() {
  /**
   * Connect to Playwright MCP server and let Claude automate a browser.
   *
   * The Playwright server runs locally (spawned by npx) and provides
   * tools like:
   * - mcp__playwright__browser_navigate — open a URL
   * - mcp__playwright__browser_click — click an element
   * - mcp__playwright__browser_snapshot — take a page snapshot
   *
   * The model sees these tools and decides how to accomplish the task.
   */
  for await (const msg of query({
    prompt:
      "Open https://example.com and tell me what the main heading says. " +
      "Then navigate to https://httpbin.org/get and show me the response headers.",
    options: {
      mcpServers: {
        playwright: {
          command: "npx",
          args: ["@playwright/mcp@latest"],
          // This runs the MCP server locally as a child process.
          // For remote servers, use:
          // url: "https://mcp.example.com/mcp",
        },
      },
      allowedTools: [
        "mcp__playwright__*", // Allow ALL tools from playwright server
      ],
    },
  })) {
    if (msg.type === "assistant") {
      for (const block of msg.content) {
        if (block.type === "text") {
          process.stdout.write(block.text);
        } else if (block.type === "tool_use") {
          console.log(`\n  → ${block.name}(${JSON.stringify(block.arguments)})`);
        }
      }
    }
  }

  // ── Remote MCP example (commented out) ───────────────────────────
  // To connect to a remote MCP server instead of a local one:
  //
  // for await (const msg of query({
  //   prompt: "Search for React hooks documentation",
  //   options: {
  //     mcpServers: {
  //       context7: {
  //         type: "remote",
  //         url: "https://mcp.context7.com/mcp",
  //         // For authenticated servers:
  //         // headers: { Authorization: "Bearer YOUR_KEY" }
  //       }
  //     },
  //     allowedTools: ["mcp__context7__*"],
  //   },
  // })) {
  //   console.log(msg);
  // }
}

main();
