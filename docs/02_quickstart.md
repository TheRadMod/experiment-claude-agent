# Agent SDK Quickstart

Source: https://platform.claude.com/docs/en/agent-sdk/quickstart
Fetched: 2026-03-25

## Prerequisites

- Python 3.10+
- Anthropic API key

## Setup

```bash
# Using uv
uv init && uv add claude-agent-sdk

# Using pip
python3 -m venv .venv && source .venv/bin/activate
pip3 install claude-agent-sdk
```

Set API key in .env file:
```
ANTHROPIC_API_KEY=your-api-key
```

## Two Main Approaches

### 1. query() - One-off interactions

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

async def main():
    async for message in query(
        prompt="Review utils.py for bugs that would cause crashes. Fix any issues you find.",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Glob"],
            permission_mode="acceptEdits",
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)
                elif hasattr(block, "name"):
                    print(f"Tool: {block.name}")
        elif isinstance(message, ResultMessage):
            print(f"Done: {message.subtype}")

asyncio.run(main())
```

### 2. ClaudeSDKClient - Continuous conversations

```python
async with ClaudeSDKClient(options=options) as client:
    await client.query("First question")
    async for message in client.receive_response():
        print(message)
    await client.query("Follow-up question")
    async for message in client.receive_response():
        print(message)
```

## Three Main Parts

1. **query**: Main entry point, returns AsyncIterator to stream messages
2. **prompt**: What you want Claude to do
3. **options**: Configuration (allowedTools, permissionMode, systemPrompt, mcpServers, etc.)

## Key Concepts

### Tools

| Tools | What the agent can do |
|-------|----------------------|
| Read, Glob, Grep | Read-only analysis |
| Read, Edit, Glob | Analyze and modify code |
| Read, Edit, Bash, Glob, Grep | Full automation |

### Permission Modes

| Mode | Behavior | Use case |
|------|----------|----------|
| acceptEdits | Auto-approves file edits | Trusted development workflows |
| bypassPermissions | Runs every tool without prompts | Sandboxed CI, fully trusted environments |
| default | Requires canUseTool callback | Custom approval flows |
| plan | No tool execution | Planning mode |

## Customization Options

### Web search:
```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Edit", "Glob", "WebSearch"],
    permission_mode="acceptEdits"
)
```

### Custom system prompt:
```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Edit", "Glob"],
    permission_mode="acceptEdits",
    system_prompt="You are a senior Python developer. Always follow PEP 8.",
)
```

### Bash access:
```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Edit", "Glob", "Bash"],
    permission_mode="acceptEdits"
)
```
