"""
test_user_message.py — Inspect what UserMessage contains

Quick test to see the full content of UserMessage objects
that appear in the agentic loop (tool results).

Output: Console + output/test_user_message.log
"""

import asyncio
import logging
import json
import os

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    UserMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
)

# ---------------------------------------------------------------------------
# Logging setup — console + file output
# ---------------------------------------------------------------------------

def setup_logging() -> logging.Logger:
    """Configure logger with both console and file handlers."""
    logger = logging.getLogger("test_user_message")
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

    # File handler — write to output/ directory
    os.makedirs("output", exist_ok=True)
    file_handler = logging.FileHandler("output/test_user_message.log", mode="w")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()


# ---------------------------------------------------------------------------
# Main inspection
# ---------------------------------------------------------------------------

async def main():
    """Run a query and inspect every UserMessage in detail."""
    logger.info("Starting query — will inspect all UserMessage objects")
    logger.info("Log file: output/test_user_message.log")

    async for message in query(
        prompt="What files are in the current directory? Give a brief one-line answer.",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Glob"]),
    ):
        message_type = type(message).__name__

        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    logger.info("[Assistant] Tool call: %s", block.name)
                elif isinstance(block, TextBlock):
                    preview = block.text[:150].replace("\n", " ")
                    logger.info("[Assistant] Text: %s", preview)

        elif isinstance(message, UserMessage):
            logger.info("[UserMessage] --- FULL INSPECTION ---")
            logger.info("  uuid: %s", getattr(message, "uuid", "N/A"))
            logger.info("  parent_tool_use_id: %s",
                        getattr(message, "parent_tool_use_id", "N/A"))

            # Content can be a string or list of content blocks
            content = message.content
            logger.info("  content type: %s", type(content).__name__)

            if isinstance(content, str):
                preview = content[:500].replace("\n", "\\n")
                logger.info("  content (str): %s", preview)
            elif isinstance(content, list):
                logger.info("  content has %d block(s):", len(content))
                for i, block in enumerate(content):
                    block_type = type(block).__name__
                    logger.info("    block[%d] type: %s", i, block_type)
                    if isinstance(block, ToolResultBlock):
                        logger.info("      tool_use_id: %s", block.tool_use_id)
                        logger.info("      is_error: %s", block.is_error)
                        if isinstance(block.content, str):
                            preview = block.content[:500].replace("\n", "\\n")
                            logger.info("      content: %s", preview)
                        elif isinstance(block.content, list):
                            logger.info("      content (list): %d items",
                                        len(block.content))
                            for j, item in enumerate(block.content):
                                logger.info("        item[%d]: %s",
                                            j, json.dumps(item, default=str)[:300])
                        else:
                            logger.info("      content: %s", block.content)
                    elif isinstance(block, TextBlock):
                        preview = block.text[:300].replace("\n", "\\n")
                        logger.info("      text: %s", preview)
                    else:
                        logger.info("      raw: %s", str(block)[:500])
            else:
                logger.info("  content (other): %s", str(content)[:500])

            # Check for tool_use_result field
            tool_result = getattr(message, "tool_use_result", None)
            if tool_result:
                logger.info("  tool_use_result: %s",
                            json.dumps(tool_result, default=str)[:500])

        elif isinstance(message, ResultMessage):
            logger.info("[Result] outcome=%s, turns=%d, cost=$%.4f",
                        message.subtype, message.num_turns,
                        message.total_cost_usd or 0)


if __name__ == "__main__":
    asyncio.run(main())
