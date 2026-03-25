"""
02_message_types.py — Parse and display all SDK message types

Demonstrates how to inspect every message type returned by the Claude Agent SDK's
agentic loop. This serves as a reference for what data is available at each stage:

Message flow for a tool-using query:
  SystemMessage (init)
    → AssistantMessage (ToolUseBlock)
      → UserMessage (ToolResultBlock)
        → AssistantMessage (TextBlock)
          → ResultMessage (final summary)

Message types:
  - SystemMessage: Session initialization metadata (cwd, session_id, tools)
  - AssistantMessage: Claude's output — contains TextBlock, ToolUseBlock, ThinkingBlock
  - UserMessage: Tool execution results — contains ToolResultBlock
  - ResultMessage: Final summary — turns, cost, duration, session_id, outcome

Output: Console + output/02_message_types.log

Usage:
    uv run 02_message_types.py
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
    SystemMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
)


# ---------------------------------------------------------------------------
# Logging setup — console + file output
# ---------------------------------------------------------------------------

def setup_logging() -> logging.Logger:
    """Configure logger with both console and file handlers."""
    logger = logging.getLogger("message_types")
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
    file_handler = logging.FileHandler("output/02_message_types.log", mode="w")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()


# ---------------------------------------------------------------------------
# Message inspection helpers
# ---------------------------------------------------------------------------

def inspect_system_message(message, message_index):
    """Log all fields of a SystemMessage."""
    logger.info("[%d] SystemMessage", message_index)
    logger.info("      subtype: %s", message.subtype)

    # The data dict contains session metadata
    data = message.data if hasattr(message, "data") else {}
    logger.info("      cwd: %s", data.get("cwd", "N/A"))
    logger.info("      session_id: %s", data.get("session_id", "N/A"))

    tools = data.get("tools", [])
    logger.info("      tools count: %d", len(tools))
    if tools:
        # Tools can be strings or dicts depending on SDK version
        tool_names = [
            t if isinstance(t, str) else t.get("name", "?")
            for t in tools[:10]
        ]
        logger.info("      tools (first 10): %s", tool_names)

    return f"SystemMessage(subtype={message.subtype}, tools={len(tools)})"


def inspect_assistant_message(message, message_index):
    """Log all blocks within an AssistantMessage."""
    logger.info("[%d] AssistantMessage (%d blocks)", message_index, len(message.content))

    block_summaries = []
    for block_index, block in enumerate(message.content):
        block_type = type(block).__name__

        if isinstance(block, TextBlock):
            truncated_text = block.text[:150].replace("\n", " ")
            logger.info("      [%d] TextBlock: \"%s%s\"",
                        block_index, truncated_text,
                        "..." if len(block.text) > 150 else "")
            block_summaries.append(f"TextBlock({len(block.text)} chars)")

        elif isinstance(block, ToolUseBlock):
            logger.info("      [%d] ToolUseBlock:", block_index)
            logger.info("            name: %s", block.name)
            logger.info("            id: %s", block.id)
            logger.info("            input keys: %s", list(block.input.keys()))
            block_summaries.append(f"ToolUseBlock({block.name})")

        else:
            # Covers ThinkingBlock and any future block types
            logger.info("      [%d] %s", block_index, block_type)
            if hasattr(block, "thinking"):
                truncated = block.thinking[:100].replace("\n", " ")
                logger.info("            thinking: \"%s...\"", truncated)
            block_summaries.append(block_type)

    return f"AssistantMessage([{', '.join(block_summaries)}])"


def inspect_user_message(message, message_index):
    """Log all blocks within a UserMessage (tool results)."""
    logger.info("[%d] UserMessage (%d blocks)", message_index, len(message.content))

    block_summaries = []
    for block_index, block in enumerate(message.content):
        block_type = type(block).__name__

        if isinstance(block, ToolResultBlock):
            logger.info("      [%d] ToolResultBlock:", block_index)
            logger.info("            tool_use_id: %s", block.tool_use_id)
            logger.info("            is_error: %s", block.is_error)
            truncated_content = str(block.content)[:150].replace("\n", " ")
            logger.info("            content: \"%s%s\"",
                        truncated_content,
                        "..." if len(str(block.content)) > 150 else "")
            status = "error" if block.is_error else "ok"
            block_summaries.append(f"ToolResultBlock({status})")
        else:
            logger.info("      [%d] %s: %s", block_index, block_type,
                        repr(block)[:100])
            block_summaries.append(block_type)

    return f"UserMessage([{', '.join(block_summaries)}])"


def inspect_result_message(message, message_index):
    """Log all fields of a ResultMessage."""
    logger.info("[%d] ResultMessage", message_index)
    logger.info("      subtype (outcome): %s", message.subtype)
    logger.info("      is_error: %s", message.is_error)
    logger.info("      num_turns: %d", message.num_turns)
    logger.info("      cost: $%.4f", message.total_cost_usd or 0)
    logger.info("      duration_ms: %s", message.duration_ms)
    logger.info("      duration_api_ms: %s", message.duration_api_ms)
    logger.info("      session_id: %s", message.session_id)

    if message.is_error:
        logger.info("      result (error): %s", message.result)

    return (f"ResultMessage(outcome={message.subtype}, "
            f"turns={message.num_turns}, cost=${message.total_cost_usd or 0:.4f})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    """
    Run a query that triggers tool use, then inspect every message type.

    The prompt asks Claude to read CLAUDE.md and summarize the project name —
    this produces the full message flow: SystemMessage → AssistantMessage
    (ToolUse) → UserMessage (ToolResult) → AssistantMessage (Text) →
    ResultMessage.
    """
    logger.info("=" * 60)
    logger.info("02_message_types.py — Inspecting all SDK message types")
    logger.info("=" * 60)

    agent_options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"],
        max_turns=4,
    )

    message_index = 0
    message_flow = []  # list of (index, summary) tuples

    async for message in query(
        prompt="Read the file CLAUDE.md and tell me the project name in one sentence.",
        options=agent_options,
    ):
        if isinstance(message, SystemMessage):
            summary = inspect_system_message(message, message_index)

        elif isinstance(message, AssistantMessage):
            summary = inspect_assistant_message(message, message_index)

        elif isinstance(message, UserMessage):
            summary = inspect_user_message(message, message_index)

        elif isinstance(message, ResultMessage):
            summary = inspect_result_message(message, message_index)

        else:
            # Catch-all for any unknown message types
            msg_type = type(message).__name__
            logger.info("[%d] UNKNOWN: %s", message_index, msg_type)
            logger.info("      repr: %s", repr(message)[:300])
            summary = f"UNKNOWN({msg_type})"

        message_flow.append((message_index, summary))
        message_index += 1

    # Print flow summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("MESSAGE FLOW SUMMARY (%d messages total)", len(message_flow))
    logger.info("=" * 60)
    for index, summary in message_flow:
        logger.info("  [%d] %s", index, summary)


if __name__ == "__main__":
    asyncio.run(main())
