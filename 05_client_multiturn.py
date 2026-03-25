"""
05_client_multiturn.py — ClaudeSDKClient for multi-turn conversations

Demonstrates ClaudeSDKClient, which maintains a persistent connection with
conversation history across multiple turns. Unlike query() (stateless,
one-shot), ClaudeSDKClient remembers previous exchanges so follow-up
questions can build on earlier context.

Key differences from query():
  query()          — stateless, fire-and-forget, each call is independent
  ClaudeSDKClient  — stateful, persistent connection, conversation memory

This script runs a 3-turn conversation analyzing a file:
  Turn 1: "Read 01_basic_query.py and list the imports"
  Turn 2: "Which of those imports are from claude_agent_sdk?" (uses context)
  Turn 3: "Are any of them unused?" (uses context from turns 1+2)

The key observation: turns 2 and 3 should work WITHOUT re-reading the file
because the conversation history is preserved in the client.

Output: Console + output/05_client_multiturn.log

Usage:
    uv run 05_client_multiturn.py
"""

import asyncio
import logging
import os

from claude_agent_sdk import (
    ClaudeSDKClient,
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
    logger = logging.getLogger("client_multiturn")
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
    file_handler = logging.FileHandler("output/05_client_multiturn.log", mode="w")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()


# ---------------------------------------------------------------------------
# Turn runner — process one turn within an active client session
# ---------------------------------------------------------------------------

async def run_turn(client, turn_number, prompt):
    """
    Send a prompt and process the response within an active ClaudeSDKClient.

    Parameters:
        client: Active ClaudeSDKClient instance (already connected)
        turn_number: Turn index for display (1, 2, 3, ...)
        prompt: The prompt string to send

    Returns:
        Dict with tools_used, text_response, turns, cost
    """
    logger.info("")
    logger.info("-" * 60)
    logger.info("Turn %d: \"%s\"", turn_number, prompt)
    logger.info("-" * 60)

    await client.query(prompt)

    tools_used = []
    text_response = ""
    turns = 0
    cost = 0.0

    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    tools_used.append(block.name)
                    logger.info("  [Tool] %s", block.name)
                elif isinstance(block, TextBlock):
                    text_response += block.text

        elif isinstance(message, UserMessage):
            for block in message.content:
                if isinstance(block, ToolResultBlock):
                    status = "ERROR" if block.is_error else "OK"
                    logger.info("  [ToolResult] %s: %s...", status,
                                str(block.content)[:80].replace("\n", " "))

        elif isinstance(message, ResultMessage):
            turns = message.num_turns
            cost = message.total_cost_usd or 0

    # Log the text response
    logger.info("  [Response]")
    for line in text_response.split("\n"):
        logger.info("    %s", line)
    logger.info("  [Done] tools=%s, turns=%d, cost=$%.4f",
                tools_used if tools_used else "none", turns, cost)

    return {
        "tools_used": tools_used,
        "text_response": text_response,
        "turns": turns,
        "cost": cost,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    """
    Run a 3-turn conversation using ClaudeSDKClient to demonstrate
    multi-turn context preservation.

    All 3 turns happen within the same client session. Turns 2 and 3
    reference information from turn 1 without re-reading the file.
    """
    logger.info("=" * 60)
    logger.info("05_client_multiturn.py — Multi-turn conversation")
    logger.info("=" * 60)

    agent_options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep"],
        disallowed_tools=["Bash"],
        max_turns=4,
    )

    turns_data = []

    async with ClaudeSDKClient(options=agent_options) as client:
        # Turn 1: Read the file and list imports
        result = await run_turn(
            client, 1,
            "Read the file 01_basic_query.py and list all its import statements. "
            "Just list them, no commentary."
        )
        turns_data.append(("Turn 1: List imports", result))

        # Turn 2: Follow-up using context from turn 1
        result = await run_turn(
            client, 2,
            "Which of those imports come from claude_agent_sdk specifically? "
            "Just list them."
        )
        turns_data.append(("Turn 2: Filter SDK imports", result))

        # Turn 3: Follow-up using context from turns 1+2
        result = await run_turn(
            client, 3,
            "Looking at the code you read earlier, are any of those SDK imports "
            "unused in the script? Explain briefly."
        )
        turns_data.append(("Turn 3: Find unused imports", result))

    # --- Summary ---
    logger.info("")
    logger.info("=" * 60)
    logger.info("MULTI-TURN SUMMARY")
    logger.info("=" * 60)

    total_cost = 0.0
    for label, data in turns_data:
        tools_str = ", ".join(data["tools_used"]) if data["tools_used"] else "none"
        logger.info("  %-30s  tools=[%-10s]  turns=%d  cost=$%.4f",
                     label, tools_str + "]", data["turns"], data["cost"])
        total_cost += data["cost"]

    logger.info("  %s", "-" * 60)
    logger.info("  Total cost: $%.4f", total_cost)

    # Key observation
    turn1_tools = turns_data[0][1]["tools_used"]
    turn2_tools = turns_data[1][1]["tools_used"]
    turn3_tools = turns_data[2][1]["tools_used"]
    logger.info("")
    logger.info("KEY OBSERVATION:")
    logger.info("  Turn 1 used tools: %s (needed to read the file)", turn1_tools)
    logger.info("  Turn 2 used tools: %s (context preserved — no re-read needed)",
                turn2_tools if turn2_tools else "none")
    logger.info("  Turn 3 used tools: %s (context preserved — no re-read needed)",
                turn3_tools if turn3_tools else "none")


if __name__ == "__main__":
    asyncio.run(main())
