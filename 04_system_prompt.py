"""
04_system_prompt.py — Customize agent behavior with system_prompt

Demonstrates how the system_prompt parameter changes Claude's behavior.
The same query is run 3 times with different system prompts to show how
persona, tone, and output structure can be controlled:

  Query 1 — No system prompt (baseline default behavior)
  Query 2 — Persona: Senior Python code reviewer (concise, critical)
  Query 3 — Constraint: Respond in exactly 3 bullet points

All queries ask Claude to review 01_basic_query.py, so the differences
in output are entirely due to the system prompt.

Output: Console + output/04_system_prompt.log

Usage:
    uv run 04_system_prompt.py
"""

import asyncio
import logging
import os

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)


# ---------------------------------------------------------------------------
# Logging setup — console + file output
# ---------------------------------------------------------------------------

def setup_logging() -> logging.Logger:
    """Configure logger with both console and file handlers."""
    logger = logging.getLogger("system_prompt")
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
    file_handler = logging.FileHandler("output/04_system_prompt.log", mode="w")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()


# ---------------------------------------------------------------------------
# Query runner
# ---------------------------------------------------------------------------

async def run_with_system_prompt(query_label, system_prompt):
    """
    Run a query with a specific system prompt and log the results.

    Parameters:
        query_label: Display label for this query
        system_prompt: The system prompt string, or None for default

    Returns:
        Dict with tools_used, text_response, turns, cost
    """
    logger.info("")
    logger.info("-" * 60)
    logger.info("%s", query_label)
    if system_prompt:
        logger.info("  system_prompt: \"%s\"", system_prompt[:100])
    else:
        logger.info("  system_prompt: None (default)")
    logger.info("-" * 60)

    agent_options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        allowed_tools=["Read"],
        disallowed_tools=["Bash"],
        max_turns=4,
    )

    # The same prompt for all queries — differences come from system_prompt
    prompt = (
        "Review the file 01_basic_query.py and give feedback. "
        "Keep your response short."
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
                    logger.info("  [Tool] %s", block.name)
                elif isinstance(block, TextBlock):
                    text_response += block.text

        elif isinstance(message, ResultMessage):
            turns = message.num_turns
            cost = message.total_cost_usd or 0

    # Log the full text response
    logger.info("  [Response]")
    for line in text_response.split("\n"):
        logger.info("    %s", line)
    logger.info("  [Done] turns=%d, cost=$%.4f, response_length=%d chars",
                turns, cost, len(text_response))

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
    Run the same review prompt with 3 different system prompts to
    demonstrate how system_prompt controls agent behavior.
    """
    logger.info("=" * 60)
    logger.info("04_system_prompt.py — System prompt demonstration")
    logger.info("=" * 60)

    queries = [
        (
            "Query 1 — Baseline (no system prompt)",
            None,
        ),
        (
            "Query 2 — Persona: Senior code reviewer",
            "You are a senior Python code reviewer with 15 years of experience. "
            "Be concise and critical. Focus on issues and improvements, not praise. "
            "Use a direct, no-nonsense tone.",
        ),
        (
            "Query 3 — Constraint: Exactly 3 bullet points",
            "You must respond in exactly 3 bullet points. No headings, no code blocks, "
            "no other formatting. Just 3 bullet points starting with '- '.",
        ),
    ]

    all_results = []
    for label, system_prompt in queries:
        result = await run_with_system_prompt(label, system_prompt)
        all_results.append((label, result))

    # --- Comparison summary ---
    logger.info("")
    logger.info("=" * 60)
    logger.info("COMPARISON SUMMARY")
    logger.info("=" * 60)
    for label, r in all_results:
        tools_str = ", ".join(r["tools_used"]) if r["tools_used"] else "none"
        logger.info("  %-45s tools=[%s]  turns=%d  cost=$%.4f  chars=%d",
                     label.split(" — ")[1] if " — " in label else label,
                     tools_str, r["turns"], r["cost"], len(r["text_response"]))

    total_cost = sum(r["cost"] for _, r in all_results)
    logger.info("  %s", "-" * 55)
    logger.info("  Total cost: $%.4f", total_cost)


if __name__ == "__main__":
    asyncio.run(main())
