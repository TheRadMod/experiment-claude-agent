"""
test_permissions.py — Investigate Bash permission behavior

Runs the same query with 3 different permission configurations
to understand how the SDK handles tool access:

Test A: permission_mode=None, allowed_tools=["Read", "Glob"] (current behavior)
Test B: permission_mode="default", allowed_tools=["Read", "Glob"]
Test C: permission_mode=None, allowed_tools=["Read", "Glob"], disallowed_tools=["Bash"]
"""

import asyncio
import logging

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolUseBlock,
)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger("test_permissions")

PROMPT = "What files are in the current directory? Give a brief one-line summary."


async def run_test(test_name: str, options: ClaudeAgentOptions):
    """Run a single query and log all messages for inspection."""
    logger.info("=" * 60)
    logger.info("TEST %s — permission_mode=%s, allowed=%s, disallowed=%s",
                test_name,
                options.permission_mode,
                options.allowed_tools,
                options.disallowed_tools)
    logger.info("=" * 60)

    try:
        async for message in query(prompt=PROMPT, options=options):
            # Log every message type we receive
            message_type = type(message).__name__
            logger.info("[%s] %s", test_name, message_type)

            if isinstance(message, SystemMessage):
                logger.info("  subtype: %s", message.subtype)

            elif isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        # Truncate long text for readability
                        text_preview = block.text[:120].replace("\n", " ")
                        logger.info("  TextBlock: %s", text_preview)
                    elif isinstance(block, ToolUseBlock):
                        logger.info("  ToolUseBlock: tool=%s, input=%s",
                                    block.name, block.input)

            elif isinstance(message, ResultMessage):
                logger.info("  outcome=%s, turns=%d, cost=$%.4f",
                            message.subtype,
                            message.num_turns,
                            message.total_cost_usd or 0)
                if message.is_error:
                    logger.error("  ERROR: %s", message.result)

    except Exception as exc:
        logger.error("[%s] Exception: %s", test_name, exc)


async def main():
    # Test A: permission_mode=None (our current script behavior)
    await run_test("A", ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"],
    ))

    # Test B: permission_mode="default" explicitly
    await run_test("B", ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"],
        permission_mode="default",
    ))

    # Test C: explicitly disallow Bash
    await run_test("C", ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"],
        disallowed_tools=["Bash"],
    ))


if __name__ == "__main__":
    asyncio.run(main())
