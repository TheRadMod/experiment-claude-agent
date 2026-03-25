"""
03_built_in_tools.py — Using Read, Glob, Grep built-in tools

Demonstrates how to direct Claude to use specific built-in tools and control
which tools are available. The SDK provides built-in tools that execute
without you implementing them: Read, Write, Edit, Bash, Glob, Grep, etc.

Key concepts:
- allowed_tools: Pre-approve specific tools (callback/prompt skipped for these)
- disallowed_tools: Block tools entirely (Claude cannot use them at all)
- When multiple tools are available, Claude chooses the best one for the task
- Blocking Bash forces Claude to use structured built-in tools instead of
  shell commands like ls, grep, cat

This script runs 4 queries, each with different tool configurations:
  Query 1 — Glob only: Find Python files
  Query 2 — Grep only: Search for import statements
  Query 3 — Read only: Read and summarize a specific file
  Query 4 — Combined: Multi-tool analysis (Claude picks tools)

Output: Console + output/03_built_in_tools.log

Usage:
    uv run 03_built_in_tools.py
"""

import asyncio
import logging
import os

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    UserMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
)


# ---------------------------------------------------------------------------
# Logging setup — console + file output
# ---------------------------------------------------------------------------

def setup_logging() -> logging.Logger:
    """Configure logger with both console and file handlers."""
    logger = logging.getLogger("built_in_tools")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    os.makedirs("output", exist_ok=True)
    file_handler = logging.FileHandler("output/03_built_in_tools.log", mode="w")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()


# ---------------------------------------------------------------------------
# Query runner — reusable helper for running a single query
# ---------------------------------------------------------------------------

async def run_tool_query(query_label, prompt, allowed_tools, disallowed_tools):
    """
    Run a single query with specific tool configuration and log results.

    Parameters:
        query_label: Display label for this query (e.g. "Query 1 — Glob")
        prompt: The prompt to send to Claude
        allowed_tools: List of pre-approved tool names
        disallowed_tools: List of blocked tool names

    Returns:
        Dict with summary: tools_used, text_response, turns, cost
    """
    logger.info("")
    logger.info("-" * 60)
    logger.info("%s", query_label)
    logger.info("  allowed_tools: %s", allowed_tools)
    logger.info("  disallowed_tools: %s", disallowed_tools)
    logger.info("-" * 60)

    agent_options = ClaudeAgentOptions(
        allowed_tools=allowed_tools,
        disallowed_tools=disallowed_tools,
        max_turns=6,
    )

    tools_used = []
    text_response = ""
    turns = 0
    cost = 0.0

    async for message in query(prompt=prompt, options=agent_options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    tools_used.append(block.name)
                    logger.info("  [Tool] %s (input keys: %s)",
                                block.name, list(block.input.keys()))
                elif isinstance(block, TextBlock):
                    text_response = block.text
                    truncated = block.text[:200].replace("\n", " ")
                    logger.info("  [Text] %s%s", truncated,
                                "..." if len(block.text) > 200 else "")

        elif isinstance(message, UserMessage):
            for block in message.content:
                if isinstance(block, ToolResultBlock):
                    status = "ERROR" if block.is_error else "OK"
                    truncated = str(block.content)[:100].replace("\n", " ")
                    logger.info("  [Result] %s: %s...", status, truncated)

        elif isinstance(message, ResultMessage):
            turns = message.num_turns
            cost = message.total_cost_usd or 0
            logger.info("  [Done] turns=%d, cost=$%.4f", turns, cost)

    summary = {
        "tools_used": tools_used,
        "text_length": len(text_response),
        "turns": turns,
        "cost": cost,
    }
    return summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    """
    Run 4 queries demonstrating different built-in tool configurations.

    Each query blocks Bash via disallowed_tools to force Claude to use
    the structured built-in tools (Glob, Grep, Read) instead of shell
    commands.
    """
    logger.info("=" * 60)
    logger.info("03_built_in_tools.py — Built-in tool demonstration")
    logger.info("=" * 60)

    all_summaries = []

    # --- Query 1: Glob only ---
    summary = await run_tool_query(
        query_label="Query 1 — Glob: Find all Python files",
        prompt=(
            "Find all Python (.py) files in the current directory and subdirectories. "
            "List them with their paths. Use the Glob tool."
        ),
        allowed_tools=["Glob"],
        disallowed_tools=["Bash"],
    )
    all_summaries.append(("Glob only", summary))

    # --- Query 2: Grep only ---
    summary = await run_tool_query(
        query_label="Query 2 — Grep: Search for import statements",
        prompt=(
            "Search for all lines containing 'from claude_agent_sdk import' across "
            "all Python files. Show the file and matching lines. Use the Grep tool."
        ),
        allowed_tools=["Grep"],
        disallowed_tools=["Bash"],
    )
    all_summaries.append(("Grep only", summary))

    # --- Query 3: Read only ---
    summary = await run_tool_query(
        query_label="Query 3 — Read: Summarize a specific file",
        prompt=(
            "Read the file 01_basic_query.py and give a 2-3 sentence summary "
            "of what it does. Use the Read tool."
        ),
        allowed_tools=["Read"],
        disallowed_tools=["Bash"],
    )
    all_summaries.append(("Read only", summary))

    # --- Query 4: Combined tools ---
    summary = await run_tool_query(
        query_label="Query 4 — Combined: Multi-tool codebase analysis",
        prompt=(
            "How many Python scripts exist in this project, and what SDK imports "
            "does each one use? Give a brief table. You can use Glob, Grep, and Read."
        ),
        allowed_tools=["Glob", "Grep", "Read"],
        disallowed_tools=["Bash"],
    )
    all_summaries.append(("Combined", summary))

    # --- Summary table ---
    logger.info("")
    logger.info("=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    total_cost = 0.0
    for label, s in all_summaries:
        tools_str = ", ".join(s["tools_used"]) if s["tools_used"] else "none"
        logger.info("  %-15s tools=[%s]  turns=%d  cost=$%.4f",
                     label, tools_str, s["turns"], s["cost"])
        total_cost += s["cost"]
    logger.info("  %s", "-" * 50)
    logger.info("  %-15s %s  total cost=$%.4f", "TOTAL", " " * 25, total_cost)


if __name__ == "__main__":
    asyncio.run(main())
