"""
06_streaming_input.py — Stream data to agent via AsyncIterable prompt

Demonstrates the AsyncIterable prompt pattern where instead of sending a
single string, you stream multiple messages to the agent over time. This is
the same mechanism used by the bidirectional control protocol (can_use_tool,
hooks) but here we use it purely for sending user messages.

Use cases for streaming input:
  - Processing data in chunks (logs, CSV rows, events)
  - Sending follow-up context mid-conversation
  - Building pipelines where data arrives over time
  - Feeding multi-part prompts incrementally

How it works:
  query() accepts AsyncIterable[dict] as the prompt. Each dict must have:
    {"type": "user", "message": {"role": "user", "content": "..."}}
  The SDK streams these to the CLI via stdin. After the iterator completes,
  stdin is closed and the agent processes everything and responds.

Important: stream_input() calls end_input() after the iterator completes,
closing stdin. This is fine for pure message streaming but breaks
can_use_tool callbacks (see test_can_use_tool.py for that workaround).

This script sends 3 messages simulating a code review pipeline:
  Message 1: A Python function with a subtle bug
  Message 2: A second function that calls the first
  Message 3: "Find the bugs"

Output: Console + output/06_streaming_input.log

Usage:
    uv run 06_streaming_input.py
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
    logger = logging.getLogger("streaming_input")
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
    file_handler = logging.FileHandler("output/06_streaming_input.log", mode="w")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()


# ---------------------------------------------------------------------------
# Code snippets to stream (simulating data arriving over time)
# ---------------------------------------------------------------------------

FUNCTION_1 = '''
def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)
'''.strip()

FUNCTION_2 = '''
def process_scores(raw_scores):
    """Process student scores: filter, average, and grade."""
    # Filter out negative scores (invalid entries)
    valid_scores = [s for s in raw_scores if s > 0]
    avg = calculate_average(valid_scores)
    if avg >= 90:
        return "A", avg
    elif avg >= 80:
        return "B", avg
    elif avg >= 70:
        return "C", avg
    else:
        return "F", avg
'''.strip()


# ---------------------------------------------------------------------------
# Message stream — the AsyncIterable that feeds the agent
# ---------------------------------------------------------------------------

async def code_review_stream():
    """
    Yield messages incrementally, simulating a code review pipeline
    where code snippets arrive one at a time.

    Each yield sends a user message to the agent. The delays between
    yields simulate data arriving over time (e.g., from a CI pipeline).
    """
    logger.info("[Stream] Sending message 1: first function...")
    yield {
        "type": "user",
        "message": {
            "role": "user",
            "content": (
                "I'm going to send you two Python functions for review. "
                "Here's the first one:\n\n```python\n" + FUNCTION_1 + "\n```"
            ),
        },
        "parent_tool_use_id": None,
        "session_id": "streaming-demo",
    }

    # Simulate delay — in a real pipeline, this could be waiting for
    # the next chunk of data from a CI system or log stream
    await asyncio.sleep(1)

    logger.info("[Stream] Sending message 2: second function...")
    yield {
        "type": "user",
        "message": {
            "role": "user",
            "content": (
                "Here's the second function that calls the first:\n\n"
                "```python\n" + FUNCTION_2 + "\n```"
            ),
        },
        "parent_tool_use_id": None,
        "session_id": "streaming-demo",
    }

    await asyncio.sleep(1)

    logger.info("[Stream] Sending message 3: review request...")
    yield {
        "type": "user",
        "message": {
            "role": "user",
            "content": (
                "Now review both functions together. Are there any bugs or "
                "edge cases that could cause errors? Be specific and concise."
            ),
        },
        "parent_tool_use_id": None,
        "session_id": "streaming-demo",
    }

    logger.info("[Stream] All messages sent — iterator completing")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    """
    Stream 3 messages to the agent via AsyncIterable and process the responses.

    IMPORTANT FINDING: Streaming input is INCREMENTAL, not batch-then-respond.
    The agent processes each streamed message as it arrives and responds
    immediately. Each message triggers a separate response cycle with its
    own SystemMessage(init) and ResultMessage. The conversation history
    accumulates — each response includes context from all previous messages.

    This means 3 streamed messages produce 3 response cycles:
      Message 1 → Response 1 (reviews function 1)
      Message 2 → Response 2 (reviews function 1+2 with context)
      Message 3 → Response 3 (full analysis with all context)
    """
    logger.info("=" * 60)
    logger.info("06_streaming_input.py — AsyncIterable prompt demo")
    logger.info("=" * 60)

    agent_options = ClaudeAgentOptions(
        disallowed_tools=["Bash", "Write", "Edit"],
        max_turns=4,
    )

    message_count = 0
    response_cycle = 0
    text_response = ""
    cycle_data = []  # collect (cycle_num, text, turns, cost) per response

    async for message in query(prompt=code_review_stream(), options=agent_options):
        message_count += 1

        if isinstance(message, SystemMessage):
            # Each streamed message triggers a new response cycle with its own init
            response_cycle += 1
            text_response = ""  # reset per cycle
            logger.info("")
            logger.info("[Cycle %d] SystemMessage (subtype=%s)",
                        response_cycle, message.subtype)

        elif isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    text_response += block.text
                elif isinstance(block, ToolUseBlock):
                    logger.info("[Cycle %d] Tool: %s", response_cycle, block.name)
                else:
                    logger.info("[Cycle %d] %s", response_cycle,
                                type(block).__name__)

        elif isinstance(message, UserMessage):
            for block in message.content:
                if isinstance(block, ToolResultBlock):
                    status = "ERROR" if block.is_error else "OK"
                    logger.info("[Cycle %d] ToolResult %s", response_cycle, status)

        elif isinstance(message, ResultMessage):
            # Log a truncated version of the response
            truncated = text_response[:200].replace("\n", " ")
            logger.info("[Cycle %d] Response (%d chars): %s%s",
                        response_cycle, len(text_response), truncated,
                        "..." if len(text_response) > 200 else "")
            logger.info("[Cycle %d] turns=%d, cost=$%.4f",
                        response_cycle, message.num_turns,
                        message.total_cost_usd or 0)

            cycle_data.append({
                "cycle": response_cycle,
                "text_length": len(text_response),
                "turns": message.num_turns,
                "cost": message.total_cost_usd or 0,
            })

    # --- Summary ---
    logger.info("")
    logger.info("=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info("  Messages streamed: 3")
    logger.info("  Response cycles: %d", len(cycle_data))
    logger.info("  Total SDK messages received: %d", message_count)

    total_cost = 0.0
    for cd in cycle_data:
        logger.info("  Cycle %d: turns=%d, cost=$%.4f, response=%d chars",
                     cd["cycle"], cd["turns"], cd["cost"], cd["text_length"])
        total_cost += cd["cost"]
    logger.info("  Total cost: $%.4f", total_cost)

    logger.info("")
    logger.info("KEY FINDING:")
    logger.info("  Streaming input is INCREMENTAL — the agent responds after each")
    logger.info("  message, not after all messages are sent. Each message creates a")
    logger.info("  new response cycle (SystemMessage + response + ResultMessage).")
    logger.info("  Context accumulates: cycle 3 has full history from cycles 1+2.")


if __name__ == "__main__":
    asyncio.run(main())
