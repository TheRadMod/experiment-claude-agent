# Sessions Guide

Source: https://platform.claude.com/docs/en/agent-sdk/sessions
Fetched: 2026-03-25

A session is the conversation history accumulated while your agent works.

## When to Use What

| What you're building | What to use |
|:---|:---|
| One-shot task | Nothing extra. One query() call handles it. |
| Multi-turn chat in one process | ClaudeSDKClient (Python) |
| Pick up after process restart | continue_conversation=True |
| Resume a specific past session | Capture session ID, pass to resume |
| Try an alternative approach | Fork the session |

## Continue vs Resume vs Fork

- **Continue**: Finds most recent session in current directory, no ID tracking
- **Resume**: Takes a specific session ID, for multiple sessions
- **Fork**: Creates new session with copy of original history, original unchanged

## Automatic Session Management (Python)

ClaudeSDKClient handles session IDs internally:

```python
async with ClaudeSDKClient(options=options) as client:
    await client.query("Analyze the auth module")
    async for message in client.receive_response():
        print_response(message)

    # Automatically continues same session
    await client.query("Now refactor it to use JWT")
    async for message in client.receive_response():
        print_response(message)
```

## Capture Session ID

```python
async for message in query(prompt="Analyze the auth module", options=options):
    if isinstance(message, ResultMessage):
        session_id = message.session_id
```

## Resume by ID

```python
async for message in query(
    prompt="Now implement the refactoring you suggested",
    options=ClaudeAgentOptions(
        resume=session_id,
        allowed_tools=["Read", "Edit", "Write"],
    ),
):
    ...
```

## Fork to Explore Alternatives

```python
async for message in query(
    prompt="Instead of JWT, implement OAuth2",
    options=ClaudeAgentOptions(
        resume=session_id,
        fork_session=True,
    ),
):
    if isinstance(message, ResultMessage):
        forked_id = message.session_id  # New session ID
```

## Session Listing and Messages

```python
from claude_agent_sdk import list_sessions, get_session_messages

for session in list_sessions(directory="/path/to/project", limit=10):
    print(f"{session.summary} ({session.session_id})")

messages = get_session_messages(session_id)
```

## Cross-Host Resume

Sessions are local to the machine. Options:
1. Move session file (~/.claude/projects/<encoded-cwd>/<session-id>.jsonl)
2. Capture results and pass into fresh session prompt
