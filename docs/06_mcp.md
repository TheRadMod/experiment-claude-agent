# MCP (Model Context Protocol) Guide

Source: https://platform.claude.com/docs/en/agent-sdk/mcp
Fetched: 2026-03-25

MCP is an open standard for connecting AI agents to external tools and data sources.

## Quick Example

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "claude-code-docs": {
            "type": "http",
            "url": "https://code.claude.com/docs/mcp",
        }
    },
    allowed_tools=["mcp__claude-code-docs__*"],
)
```

## Tool Naming Convention

MCP tools follow: `mcp__<server-name>__<tool-name>`
Example: mcp__github__list_issues

Use wildcards: `mcp__github__*` to allow all tools from a server.

## Transport Types

### stdio servers (local processes)
```python
options = ClaudeAgentOptions(
    mcp_servers={
        "github": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_TOKEN": os.environ["GITHUB_TOKEN"]},
        }
    },
)
```

### HTTP/SSE servers (remote)
```python
options = ClaudeAgentOptions(
    mcp_servers={
        "remote-api": {
            "type": "sse",
            "url": "https://api.example.com/mcp/sse",
            "headers": {"Authorization": f"Bearer {token}"},
        }
    },
)
```

### SDK MCP Servers (in-process)

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("add", "Add two numbers", {"a": float, "b": float})
async def add(args):
    return {"content": [{"type": "text", "text": f"Sum: {args['a'] + args['b']}"}]}

calculator = create_sdk_mcp_server(
    name="calculator",
    version="2.0.0",
    tools=[add],
)

options = ClaudeAgentOptions(
    mcp_servers={"calc": calculator},
    allowed_tools=["mcp__calc__add"],
)
```

Benefits of SDK MCP servers:
- No subprocess management
- Better performance (no IPC overhead)
- Simpler deployment
- Easier debugging
- Type safety

## Mixed Server Support

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "internal": sdk_server,       # In-process
        "external": {                  # External subprocess
            "type": "stdio",
            "command": "external-server"
        }
    }
)
```

## Config File (.mcp.json)

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
    }
  }
}
```

## Error Handling

Check MCP status in init message:
```python
if isinstance(message, SystemMessage) and message.subtype == "init":
    failed = [s for s in message.data.get("mcp_servers", []) if s.get("status") != "connected"]
    if failed:
        print(f"Failed: {failed}")
```
