/**
 * Example 04: Custom Tools
 *
 * You can create your own tools — any TypeScript/JavaScript function that the
 * model can call. A "tool" is just a function: it can do anything a computer
 * can do — call APIs, query databases, run commands, control hardware, anything.
 *
 * This example creates two custom tools:
 * 1. calculate — evaluate a math expression (local computation)
 * 2. getWeather — fetch weather data (simulated API call)
 *
 * The tool() function registers your function with a name, description, and
 * argument schema. The model uses the description to decide WHEN to call it.
 *
 * Concepts introduced:
 * - tool() — register a TypeScript function as a tool
 * - createMcpServer() — host tools via MCP (Model Context Protocol)
 * - MCP tool naming — "mcp__<server>__<tool>" convention
 * - Tool as a function — it can call APIs, query databases, run commands, anything
 */

import { query, tool, createMcpServer } from "@anthropic-ai/claude-agent-sdk";
import type { AssistantMessage } from "@anthropic-ai/claude-agent-sdk";

// ─── Tool 1: Calculate ───────────────────────────────────────────────
// This tool evaluates a math expression. It runs LOCALLY on your machine.
// In real use, this could be any function: database query, API call, etc.

const calculate = tool(
  "calculate",
  "Evaluate a math expression. Supports +, -, *, /, **, and parentheses.",
  { expression: { type: "string" } },
  async (args) => {
    try {
      // In production, use a proper math parser instead of Function()
      const result = Function(`"use strict"; return (${args.expression})`)();
      return { content: [{ type: "text" as const, text: String(result) }] };
    } catch (e) {
      return { content: [{ type: "text" as const, text: `Error: ${e}` }] };
    }
  }
);

// ─── Tool 2: Get Weather ─────────────────────────────────────────────
// This tool simulates an API call. In real use, this could call
// weather.com, OpenWeatherMap, or any HTTP endpoint.

const getWeather = tool(
  "get_weather",
  "Get the current weather for a city. Returns temperature and conditions.",
  { city: { type: "string" } },
  async (args) => {
    // Simulated response — in production, call a real weather API:
    // const resp = await fetch(`https://api.openweathermap.org/...?q=${args.city}`);
    // const data = await resp.json();
    // return { content: [{ type: "text", text: data.weather[0].description }] };
    return {
      content: [{
        type: "text" as const,
        text: `Weather in ${args.city}: 72°F (22°C), sunny, humidity 45%`,
      }],
    };
  }
);

// ─── Tool 3: Database Query (simulated) ──────────────────────────────
// This tool queries a database. In real use, connect to PostgreSQL,
// MongoDB, SQLite, Redis, or any data store.

const queryDb = tool(
  "query_db",
  "Query the users database. Pass a SQL-like query string.",
  { query: { type: "string" } },
  async (args) => {
    // Simulated — in production:
    // import pg from "pg";
    // const client = new pg.Client("postgresql://...");
    // await client.connect();
    // const result = await client.query(args.query);
    // return { content: [{ type: "text", text: JSON.stringify(result.rows) }] };
    return {
      content: [{
        type: "text" as const,
        text: `Query result for '${args.query}': 42 users found`,
      }],
    };
  }
);

async function main() {
  /**
   * Create a server with all three tools and let the model use them.
   *
   * The model sees the tool descriptions and decides which to call:
   * - "What's 15 * 7 + 3?" → calls calculate
   * - "What's the weather in NYC?" → calls get_weather
   * - "How many users do we have?" → calls query_db
   *
   * It can also chain them: "Get the weather in London, then calculate
   * the temperature in Celsius" → calls getWeather, then calculate.
   */
  const server = createMcpServer("mytools", [calculate, getWeather, queryDb]);

  for await (const msg of query({
    prompt: "What's 15 * 7 + 3? Also, what's the weather in NYC? And how many users are in the database?",
    options: {
      mcpServers: { mytools: server },       // Register our tool server
      allowedTools: ["mcp__mytools__*"],     // Allow all tools from our server
    },
  })) {
    if (msg.type === "assistant") {
      for (const block of msg.content) {
        if (block.type === "text") {
          console.log(`\n${block.text}`);
        } else if (block.type === "tool_use") {
          console.log(`\n  → Tool: ${block.name}(${JSON.stringify(block.arguments)})`);
        }
      }
    }
  }
}

main();
