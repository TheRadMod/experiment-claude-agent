# Subagents Guide

Source: https://platform.claude.com/docs/en/agent-sdk/subagents
Fetched: 2026-03-25

Subagents are separate agent instances that your main agent can spawn for focused subtasks.

## Benefits

1. **Context isolation** - Fresh conversation, only final message returns to parent
2. **Parallelization** - Multiple subagents run concurrently
3. **Specialized instructions** - Tailored system prompts with specific expertise
4. **Tool restrictions** - Limited to specific tools

## Three Ways to Create Subagents

1. **Programmatic**: agents parameter in query() options (recommended for SDK)
2. **Filesystem-based**: markdown files in .claude/agents/
3. **Built-in**: Claude can spawn general-purpose subagent via Agent tool

## Programmatic Definition

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

async for message in query(
    prompt="Review the authentication module for security issues",
    options=ClaudeAgentOptions(
        allowed_tools=["Read", "Grep", "Glob", "Agent"],  # Agent tool required!
        agents={
            "code-reviewer": AgentDefinition(
                description="Expert code review specialist.",
                prompt="You are a code review specialist...",
                tools=["Read", "Grep", "Glob"],
                model="sonnet",
            ),
            "test-runner": AgentDefinition(
                description="Runs and analyzes test suites.",
                prompt="You are a test execution specialist...",
                tools=["Bash", "Read", "Grep"],
            ),
        },
    ),
):
    ...
```

## AgentDefinition Fields

| Field | Type | Required | Description |
|:------|:-----|:---------|:------------|
| description | str | Yes | When to use this agent |
| prompt | str | Yes | System prompt for the agent |
| tools | list[str] | No | Allowed tools (inherits all if omitted) |
| model | str | No | 'sonnet', 'opus', 'haiku', 'inherit' |

Note: Subagents cannot spawn their own subagents.

## What Subagents Inherit

| Receives | Does not receive |
|:---|:---|
| Its own system prompt + Agent tool's prompt | Parent's conversation history |
| Project CLAUDE.md | Parent's system prompt |
| Tool definitions (subset or inherited) | Skills (unless listed) |

## Invocation

- **Automatic**: Claude decides based on description
- **Explicit**: "Use the code-reviewer agent to check..."
- **Dynamic**: Factory functions to customize at runtime

## Common Tool Combinations

| Use case | Tools |
|:---------|:------|
| Read-only analysis | Read, Grep, Glob |
| Test execution | Bash, Read, Grep |
| Code modification | Read, Edit, Write, Grep, Glob |
| Full access | Omit tools field |

## Resuming Subagents

1. Capture session_id from ResultMessage
2. Extract agentId from message content
3. Resume with resume=sessionId and include agentId in prompt

## Detecting Subagent Invocation

Check for ToolUseBlock where name is "Agent". Messages from within a subagent include parent_tool_use_id.
