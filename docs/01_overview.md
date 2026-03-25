# Agent SDK Overview

Source: https://platform.claude.com/docs/en/agent-sdk/overview
Fetched: 2026-03-25

Build production AI agents with Claude Code as a library.

The Claude Code SDK has been renamed to the Claude Agent SDK.

Build AI agents that autonomously read files, run commands, search the web, edit code, and more. The Agent SDK gives you the same tools, agent loop, and context management that power Claude Code, programmable in Python and TypeScript.

## Quick Example

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="Find and fix the bug in auth.py",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Edit", "Bash"]),
    ):
        print(message)

asyncio.run(main())
```

## Installation

```bash
pip install claude-agent-sdk
```

## Set API Key

```bash
export ANTHROPIC_API_KEY=your-api-key
```

Also supports:
- Amazon Bedrock: set CLAUDE_CODE_USE_BEDROCK=1
- Google Vertex AI: set CLAUDE_CODE_USE_VERTEX=1
- Microsoft Azure: set CLAUDE_CODE_USE_FOUNDRY=1

## Built-in Tools

| Tool | What it does |
|------|--------------|
| Read | Read any file in the working directory |
| Write | Create new files |
| Edit | Make precise edits to existing files |
| Bash | Run terminal commands, scripts, git operations |
| Glob | Find files by pattern |
| Grep | Search file contents with regex |
| WebSearch | Search the web for current information |
| WebFetch | Fetch and parse web page content |
| AskUserQuestion | Ask the user clarifying questions |

## Capabilities

1. **Built-in tools** - Read files, run commands, search codebases out of the box
2. **Hooks** - Run custom code at key points in the agent lifecycle (PreToolUse, PostToolUse, Stop, etc.)
3. **Subagents** - Spawn specialized agents to handle focused subtasks
4. **MCP** - Connect to external systems via Model Context Protocol
5. **Permissions** - Control exactly which tools your agent can use
6. **Sessions** - Maintain context across multiple exchanges, resume or fork sessions

## Claude Code Features (via settings)

Set `setting_sources=["project"]` to use:
- Skills: Specialized capabilities defined in Markdown (.claude/skills/SKILL.md)
- Slash commands: Custom commands (.claude/commands/*.md)
- Memory: Project context and instructions (CLAUDE.md)
- Plugins: Extend with custom commands, agents, and MCP servers

## Agent SDK vs Client SDK

- Client SDK: You implement the tool loop yourself
- Agent SDK: Claude handles tools autonomously

## Agent SDK vs Claude Code CLI

| Use case | Best choice |
|----------|-------------|
| Interactive development | CLI |
| CI/CD pipelines | SDK |
| Custom applications | SDK |
| One-off tasks | CLI |
| Production automation | SDK |
