"""
01_basic_query.py — Simplest Claude Agent SDK interaction

Demonstrates the core pattern of the Claude Agent SDK:
1. Import query() and ClaudeAgentOptions
2. Call query() with a prompt and minimal options
3. Iterate the async response stream (AsyncIterator[Message])
4. Parse message types to extract useful output

This is the foundation that every other script builds upon.

Prerequisites:
    - ANTHROPIC_API_KEY environment variable set
    - pip install claude-agent-sdk

Usage:
    python3 01_basic_query.py
"""

import asyncio
import logging

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)

# ---------------------------------------------------------------------------
# Logging setup — all experiment scripts use the logging module with console
# output, as decided in our script conventions.
# ---------------------------------------------------------------------------

def setup_logging() -> logging.Logger:
    """Configure and return a logger with console output."""
    logger = logging.getLogger("basic_query")
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


logger = setup_logging()


# ---------------------------------------------------------------------------
# Main agent interaction
# ---------------------------------------------------------------------------

async def main():
    """
    Run a simple one-shot query using the Claude Agent SDK.

    query() creates a new session each time it is called. It returns an
    AsyncIterator[Message] that yields messages as Claude works — text
    responses, tool calls, tool results, and a final ResultMessage.
    """
    logger.info("Starting basic query...")

    # ClaudeAgentOptions configures the agent's behavior.
    # allowed_tools pre-approves these tools so they run without permission
    # prompts. We use only read-only tools here for safety.
    agent_options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"],
    )

    # query() is the main entry point. It returns an async iterator that
    # streams messages as Claude thinks, calls tools, and produces output.
    async for message in query(
        prompt="What files are in the current directory? Give a brief summary.",
        options=agent_options,
    ):
        # --- AssistantMessage: Claude's reasoning and tool calls ---
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    # TextBlock contains Claude's natural language response
                    print(f"\n{block.text}")
                elif isinstance(block, ToolUseBlock):
                    # ToolUseBlock means Claude is calling a built-in tool
                    logger.info("Tool called: %s", block.name)

        # --- ResultMessage: final summary when the agent finishes ---
        elif isinstance(message, ResultMessage):
            logger.info("--- Agent finished ---")
            logger.info("Session ID : %s", message.session_id)
            logger.info("Outcome    : %s", message.subtype)
            logger.info("Turns      : %d", message.num_turns)
            logger.info("Duration   : %d ms", message.duration_ms)
            logger.info("API time   : %d ms", message.duration_api_ms)

            if message.total_cost_usd is not None:
                logger.info("Cost       : $%.4f", message.total_cost_usd)

            if message.is_error:
                logger.error("Error result: %s", message.result)


if __name__ == "__main__":
    asyncio.run(main())
