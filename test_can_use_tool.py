"""
test_can_use_tool.py — Implement canUseTool callback for proper tool restriction

Demonstrates how to use the can_use_tool callback to act as a gatekeeper
for tool access. Unlike allowed_tools (which only pre-approves), this
callback receives every unapproved tool request and makes a deny/allow
decision — making it the proper way to restrict which tools an agent can use.

Key learnings from earlier tests:
- allowed_tools is a pre-approval list, NOT a restriction
- permission_mode="default" without a callback still lets tools through
- disallowed_tools blocks tools but doesn't give you programmatic control
- can_use_tool callback is the right approach for custom permission logic

Important notes:
- ClaudeSDKClient keeps stdin open (no stream_input race), so the control
  protocol works for bidirectional can_use_tool communication.
- The CLI auto-approves "safe" Bash commands (e.g. ls, cat) internally via
  bashToolHasPermission — the callback only fires for tools that actually
  require permission (e.g. Write, Edit, or dangerous Bash commands).
- Requires SDK installed from GitHub main branch (response format fix for
  Issue #200 is not yet released to PyPI as of v0.1.50).

Output: Console + output/test_can_use_tool.log

Usage:
    uv run test_can_use_tool.py
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
    PermissionResultAllow,
    PermissionResultDeny,
)


# ---------------------------------------------------------------------------
# Logging setup — console + file output
# ---------------------------------------------------------------------------

def setup_logging() -> logging.Logger:
    """Configure logger with both console and file handlers."""
    logger = logging.getLogger("test_can_use_tool")
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
    file_handler = logging.FileHandler("output/test_can_use_tool.log", mode="w")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()


# ---------------------------------------------------------------------------
# canUseTool callback — the gatekeeper
# ---------------------------------------------------------------------------

# Only the Write tool is allowed through the callback. Everything else is denied.
# Note: pre-approved tools (allowed_tools) bypass this callback entirely.
CALLBACK_PERMITTED_TOOLS = {"Write"}


async def custom_can_use_tool(tool_name, tool_input, context):
    """
    Callback invoked for every tool request not already pre-approved by
    allowed_tools and not auto-approved by the CLI's internal heuristics.

    Parameters:
        tool_name: Name of the tool being requested (e.g. "Write", "Edit")
        tool_input: Dict of the tool's input arguments
        context: ToolPermissionContext with session metadata

    Returns:
        PermissionResultAllow or PermissionResultDeny
    """
    logger.info("[canUseTool] Request for tool: '%s'", tool_name)
    logger.info("[canUseTool]   input keys: %s", list(tool_input.keys()))

    if tool_name in CALLBACK_PERMITTED_TOOLS:
        logger.info("[canUseTool]   -> ALLOWED (in callback permit list)")
        return PermissionResultAllow()

    reason = f"Tool '{tool_name}' is not in the callback permitted set: {CALLBACK_PERMITTED_TOOLS}"
    logger.info("[canUseTool]   -> DENIED (%s)", reason)
    return PermissionResultDeny(message=reason)


# ---------------------------------------------------------------------------
# Main test
# ---------------------------------------------------------------------------

async def main():
    """
    Run two queries to demonstrate the canUseTool callback:

    Query 1 (ALLOW): Ask Claude to write a file — Write tool is in our
    callback permit list, so the callback allows it.

    Query 2 (DENY): Ask Claude to edit a file — Edit tool is NOT in our
    callback permit list, so the callback denies it.

    Configuration:
    - allowed_tools=["Read", "Glob"] — pre-approved, callback never sees these
    - permission_mode="default" — unapproved tools route to canUseTool
    - can_use_tool=custom_can_use_tool — our gatekeeper function
    """
    test_file_path = "/tmp/test_can_use_tool.txt"

    logger.info("=" * 60)
    logger.info("Test: canUseTool callback as tool gatekeeper")
    logger.info("  Pre-approved (allowed_tools): Read, Glob")
    logger.info("  Callback permit list: %s", CALLBACK_PERMITTED_TOOLS)
    logger.info("  permission_mode: default")
    logger.info("=" * 60)

    agent_options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"],
        permission_mode="default",
        can_use_tool=custom_can_use_tool,
        max_turns=4,
    )

    # --- Query 1: Write (should be ALLOWED by callback) ---
    logger.info("")
    logger.info("-" * 60)
    logger.info("QUERY 1: Write a file (expect: callback ALLOWS)")
    logger.info("-" * 60)

    async with ClaudeSDKClient(options=agent_options) as client:
        await client.query(
            f'Create a file at {test_file_path} with the content "hello from canUseTool test". '
            f'Use the Write tool.'
        )

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        logger.info("[Assistant] Text: %s",
                                    block.text[:200].replace("\n", " "))
                    elif isinstance(block, ToolUseBlock):
                        logger.info("[Assistant] Tool call: %s", block.name)
                    else:
                        logger.info("[Assistant] Block: %s", type(block).__name__)

            elif isinstance(message, UserMessage):
                for block in message.content:
                    if isinstance(block, ToolResultBlock):
                        status = "ERROR" if block.is_error else "OK"
                        logger.info("[ToolResult] %s: %s", status,
                                    str(block.content)[:150])

            elif isinstance(message, ResultMessage):
                logger.info("--- Query 1 finished ---")
                logger.info("  outcome: %s", message.subtype)
                logger.info("  turns: %d", message.num_turns)
                logger.info("  cost: $%.4f", message.total_cost_usd or 0)

    # Verify the file was created
    if os.path.exists(test_file_path):
        with open(test_file_path) as f:
            logger.info("  FILE VERIFIED: '%s'", f.read().strip())
    else:
        logger.warning("  FILE NOT CREATED")

    # --- Query 2: Edit (should be DENIED by callback) ---
    logger.info("")
    logger.info("-" * 60)
    logger.info("QUERY 2: Edit the file (expect: callback DENIES)")
    logger.info("-" * 60)

    async with ClaudeSDKClient(options=agent_options) as client:
        await client.query(
            f'Edit the file at {test_file_path} to change "hello" to "goodbye". '
            f'Use the Edit tool.'
        )

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        logger.info("[Assistant] Text: %s",
                                    block.text[:200].replace("\n", " "))
                    elif isinstance(block, ToolUseBlock):
                        logger.info("[Assistant] Tool call: %s", block.name)
                    else:
                        logger.info("[Assistant] Block: %s", type(block).__name__)

            elif isinstance(message, UserMessage):
                for block in message.content:
                    if isinstance(block, ToolResultBlock):
                        status = "ERROR" if block.is_error else "OK"
                        logger.info("[ToolResult] %s: %s", status,
                                    str(block.content)[:150])

            elif isinstance(message, ResultMessage):
                logger.info("--- Query 2 finished ---")
                logger.info("  outcome: %s", message.subtype)
                logger.info("  turns: %d", message.num_turns)
                logger.info("  cost: $%.4f", message.total_cost_usd or 0)

    # Verify the file was NOT edited
    if os.path.exists(test_file_path):
        with open(test_file_path) as f:
            content = f.read().strip()
            if "goodbye" in content:
                logger.warning("  FILE WAS EDITED (callback deny failed): '%s'", content)
            else:
                logger.info("  FILE UNCHANGED (callback deny worked): '%s'", content)
        os.remove(test_file_path)
        logger.info("  Cleaned up test file")
    else:
        logger.info("  File does not exist (expected if Write was also denied)")


if __name__ == "__main__":
    asyncio.run(main())
