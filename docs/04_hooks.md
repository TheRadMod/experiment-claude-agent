# Hooks Guide

Source: https://platform.claude.com/docs/en/agent-sdk/hooks
Fetched: 2026-03-25

Hooks are callback functions that run your code in response to agent events.

## What Hooks Can Do

- Block dangerous operations before they execute
- Log and audit every tool call
- Transform inputs and outputs
- Require human approval for sensitive actions
- Track session lifecycle

## How Hooks Work

1. An event fires (PreToolUse, PostToolUse, etc.)
2. SDK collects registered hooks
3. Matchers filter which hooks run
4. Callback functions execute
5. Callback returns a decision (allow, block, modify, inject context)

## Available Hook Events (Python SDK)

| Hook Event | What triggers it |
|------------|------------------|
| PreToolUse | Tool call request (can block or modify) |
| PostToolUse | Tool execution result |
| PostToolUseFailure | Tool execution failure |
| UserPromptSubmit | User prompt submission |
| Stop | Agent execution stop |
| SubagentStart | Subagent initialization |
| SubagentStop | Subagent completion |
| PreCompact | Conversation compaction request |
| PermissionRequest | Permission dialog would be displayed |
| Notification | Agent status messages |

Note: SessionStart, SessionEnd are TypeScript-only for SDK callbacks.

## Configuration

```python
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [HookMatcher(matcher="Bash", hooks=[my_callback])]
    }
)
```

## Matchers

- matcher: regex pattern matched against tool name
- Built-in tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch, Agent
- MCP tools: mcp__<server>__<action>
- Omit matcher to run for all events of that type

## Callback Function Signature

```python
async def my_hook(
    input_data: dict[str, Any],   # Event details
    tool_use_id: str | None,       # Correlates Pre/Post events
    context: HookContext           # Reserved for future use
) -> dict[str, Any]:
    return {}  # Empty = allow
```

## Hook Output Fields

- Top-level: systemMessage (injects into conversation), continue_ (keep running)
- hookSpecificOutput: permissionDecision ("allow"/"deny"/"ask"), permissionDecisionReason, updatedInput

## Key Examples

### Block dangerous operations
```python
async def protect_env_files(input_data, tool_use_id, context):
    file_path = input_data["tool_input"].get("file_path", "")
    if file_path.split("/")[-1] == ".env":
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "deny",
                "permissionDecisionReason": "Cannot modify .env files",
            }
        }
    return {}
```

### Modify tool input
```python
async def redirect_to_sandbox(input_data, tool_use_id, context):
    if input_data["tool_name"] == "Write":
        original_path = input_data["tool_input"].get("file_path", "")
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "allow",
                "updatedInput": {
                    **input_data["tool_input"],
                    "file_path": f"/sandbox{original_path}",
                },
            }
        }
    return {}
```

### Auto-approve specific tools
```python
async def auto_approve_read_only(input_data, tool_use_id, context):
    read_only_tools = ["Read", "Glob", "Grep"]
    if input_data["tool_name"] in read_only_tools:
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "allow",
            }
        }
    return {}
```

### Chain multiple hooks
```python
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(hooks=[rate_limiter]),
            HookMatcher(hooks=[authorization_check]),
            HookMatcher(hooks=[input_sanitizer]),
            HookMatcher(hooks=[audit_logger]),
        ]
    }
)
```

### Async (fire-and-forget) hooks
```python
async def async_hook(input_data, tool_use_id, context):
    asyncio.create_task(send_to_logging_service(input_data))
    return {"async_": True, "asyncTimeout": 30000}
```

## Priority Rules

deny > ask > allow (if multiple hooks apply)
