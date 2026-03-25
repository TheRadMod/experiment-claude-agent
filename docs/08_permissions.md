# Permissions Guide

Source: https://platform.claude.com/docs/en/agent-sdk/permissions
Fetched: 2026-03-25

## Permission Evaluation Order

1. Hooks (can allow, deny, or continue)
2. Deny rules (disallowed_tools)
3. Permission mode
4. Allow rules (allowed_tools)
5. canUseTool callback

## Allow and Deny Rules

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep"],     # Auto-approved
    disallowed_tools=["Bash"],           # Always denied
)
```

- allowed_tools: pre-approves listed tools. Unlisted tools fall through.
- disallowed_tools: always blocked, even in bypassPermissions mode.

## Permission Modes

| Mode | Description |
|:-----|:------------|
| default | No auto-approvals; triggers canUseTool callback |
| acceptEdits | Auto-approves file edits and filesystem operations |
| bypassPermissions | All tools run without prompts (use with caution) |
| plan | No tool execution; planning only |

### acceptEdits Details

Auto-approved:
- File edits (Edit, Write tools)
- Filesystem commands: mkdir, touch, rm, mv, cp

### bypassPermissions Warning

- allowed_tools does NOT constrain this mode
- Subagents inherit this mode and it cannot be overridden
- Only use in sandboxed/trusted environments

## canUseTool Callback

```python
CanUseTool = Callable[
    [str, dict[str, Any], ToolPermissionContext],
    Awaitable[PermissionResult]
]
```

Returns PermissionResultAllow or PermissionResultDeny.

## Dynamic Permission Mode

```python
q = query(prompt="...", options=ClaudeAgentOptions(permission_mode="default"))
await q.set_permission_mode("acceptEdits")  # Change mid-session
```
