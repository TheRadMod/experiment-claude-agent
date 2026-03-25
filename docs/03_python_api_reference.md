# Python Agent SDK API Reference

Source: https://platform.claude.com/docs/en/agent-sdk/python
Fetched: 2026-03-25

## Core Functions

### query()

```python
async def query(
    *,
    prompt: str | AsyncIterable[dict[str, Any]],
    options: ClaudeAgentOptions | None = None,
    transport: Transport | None = None
) -> AsyncIterator[Message]
```

Creates a new session for each interaction. Returns AsyncIterator[Message].

### tool() Decorator

```python
def tool(
    name: str,
    description: str,
    input_schema: type | dict[str, Any],
    annotations: ToolAnnotations | None = None
) -> Callable[[Callable[[Any], Awaitable[dict[str, Any]]]], SdkMcpTool[Any]]
```

Define MCP tools with type safety.

Example:
```python
from claude_agent_sdk import tool

@tool("greet", "Greet a user", {"name": str})
async def greet(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Hello, {args['name']}!"}]}
```

### create_sdk_mcp_server()

```python
def create_sdk_mcp_server(
    name: str,
    version: str = "1.0.0",
    tools: list[SdkMcpTool[Any]] | None = None
) -> McpSdkServerConfig
```

Create in-process MCP server.

### list_sessions()

```python
def list_sessions(
    directory: str | None = None,
    limit: int | None = None,
    include_worktrees: bool = True
) -> list[SDKSessionInfo]
```

### get_session_messages()

```python
def get_session_messages(
    session_id: str,
    directory: str | None = None,
    limit: int | None = None,
    offset: int = 0
) -> list[SessionMessage]
```

## ClaudeSDKClient Class

```python
class ClaudeSDKClient:
    def __init__(self, options: ClaudeAgentOptions | None = None, transport: Transport | None = None)
    async def connect(self, prompt: str | AsyncIterable[dict] | None = None) -> None
    async def query(self, prompt: str | AsyncIterable[dict], session_id: str = "default") -> None
    async def receive_messages(self) -> AsyncIterator[Message]
    async def receive_response(self) -> AsyncIterator[Message]
    async def interrupt(self) -> None
    async def set_permission_mode(self, mode: str) -> None
    async def set_model(self, model: str | None = None) -> None
    async def rewind_files(self, user_message_id: str) -> None
    async def get_mcp_status(self) -> list[McpServerStatus]
    async def add_mcp_server(self, name: str, config: McpServerConfig) -> None
    async def remove_mcp_server(self, name: str) -> None
    async def get_server_info(self) -> dict[str, Any] | None
    async def disconnect(self) -> None
```

Supports async context manager:
```python
async with ClaudeSDKClient() as client:
    await client.query("Hello Claude")
    async for message in client.receive_response():
        print(message)
```

## ClaudeAgentOptions

```python
@dataclass
class ClaudeAgentOptions:
    # Tool Configuration
    tools: list[str] | ToolsPreset | None = None
    allowed_tools: list[str] = field(default_factory=list)
    disallowed_tools: list[str] = field(default_factory=list)

    # System & Prompts
    system_prompt: str | SystemPromptPreset | None = None

    # MCP Servers
    mcp_servers: dict[str, McpServerConfig] | str | Path = field(default_factory=dict)

    # Permissions
    permission_mode: PermissionMode | None = None
    can_use_tool: CanUseTool | None = None

    # Model & Budget
    model: str | None = None
    fallback_model: str | None = None
    max_turns: int | None = None
    max_budget_usd: float | None = None

    # Conversation Control
    continue_conversation: bool = False
    resume: str | None = None
    fork_session: bool = False

    # Output
    output_format: dict[str, Any] | None = None
    include_partial_messages: bool = False

    # Environment
    cwd: str | Path | None = None
    env: dict[str, str] = field(default_factory=dict)
    add_dirs: list[str | Path] = field(default_factory=list)

    # Advanced
    cli_path: str | Path | None = None
    settings: str | None = None
    setting_sources: list[SettingSource] | None = None
    extra_args: dict[str, str | None] = field(default_factory=dict)
    max_buffer_size: int | None = None
    stderr: Callable[[str], None] | None = None

    # Hooks & Features
    hooks: dict[HookEvent, list[HookMatcher]] | None = None
    user: str | None = None
    agents: dict[str, AgentDefinition] | None = None
    plugins: list[SdkPluginConfig] = field(default_factory=list)

    # Thinking
    thinking: ThinkingConfig | None = None
    effort: Literal["low", "medium", "high", "max"] | None = None

    # Advanced Features
    betas: list[SdkBeta] = field(default_factory=list)
    permission_prompt_tool_name: str | None = None
    enable_file_checkpointing: bool = False
    sandbox: SandboxSettings | None = None
```

## Message Types

```python
Message = UserMessage | AssistantMessage | SystemMessage | ResultMessage | StreamEvent
```

### UserMessage
```python
@dataclass
class UserMessage:
    content: str | list[ContentBlock]
    uuid: str | None = None
    parent_tool_use_id: str | None = None
    tool_use_result: dict[str, Any] | None = None
```

### AssistantMessage
```python
@dataclass
class AssistantMessage:
    content: list[ContentBlock]
    model: str
    parent_tool_use_id: str | None = None
    error: AssistantMessageError | None = None
```

### ResultMessage
```python
@dataclass
class ResultMessage:
    subtype: str
    duration_ms: int
    duration_api_ms: int
    is_error: bool
    num_turns: int
    session_id: str
    total_cost_usd: float | None = None
    usage: dict[str, Any] | None = None
    result: str | None = None
    stop_reason: str | None = None
    structured_output: Any = None
```

### Content Blocks
```python
@dataclass
class TextBlock:
    text: str

@dataclass
class ThinkingBlock:
    thinking: str
    signature: str

@dataclass
class ToolUseBlock:
    id: str
    name: str
    input: dict[str, Any]

@dataclass
class ToolResultBlock:
    tool_use_id: str
    content: str | list[dict[str, Any]] | None = None
    is_error: bool | None = None
```

## Permission Types

```python
PermissionMode = Literal["default", "acceptEdits", "plan", "bypassPermissions"]

CanUseTool = Callable[
    [str, dict[str, Any], ToolPermissionContext], Awaitable[PermissionResult]
]
```

## Hook Types

```python
HookEvent = Literal[
    "PreToolUse", "PostToolUse", "PostToolUseFailure",
    "UserPromptSubmit", "Stop", "SubagentStop",
    "PreCompact", "Notification", "SubagentStart", "PermissionRequest",
]

@dataclass
class HookMatcher:
    matcher: str | None = None
    hooks: list[HookCallback] = field(default_factory=list)
    timeout: float | None = None  # seconds (default: 60)

HookCallback = Callable[
    [HookInput, str | None, HookContext], Awaitable[HookJSONOutput]
]
```

## MCP Server Configuration

```python
McpServerConfig = McpStdioServerConfig | McpSSEServerConfig | McpHttpServerConfig | McpSdkServerConfig

class McpStdioServerConfig(TypedDict):
    type: NotRequired[Literal["stdio"]]
    command: str
    args: NotRequired[list[str]]
    env: NotRequired[dict[str, str]]

class McpSSEServerConfig(TypedDict):
    type: Literal["sse"]
    url: str
    headers: NotRequired[dict[str, str]]

class McpHttpServerConfig(TypedDict):
    type: Literal["http"]
    url: str
    headers: NotRequired[dict[str, str]]
```

## Error Types

```python
class ClaudeSDKError(Exception): ...
class CLINotFoundError(CLIConnectionError): ...
class CLIConnectionError(ClaudeSDKError): ...
class ProcessError(ClaudeSDKError):
    exit_code: int | None
    stderr: str | None
class CLIJSONDecodeError(ClaudeSDKError):
    line: str
    original_error: Exception
```

## Built-in Tools Reference

| Tool | Input | Notes |
|------|-------|-------|
| Agent | {description, prompt, subagent_type} | Spawn subagent |
| Bash | {command, timeout?, description?} | Execute shell command |
| Read | {file_path, offset?, limit?} | Read file |
| Write | {file_path, content} | Create/overwrite file |
| Edit | {file_path, old_string, new_string, replace_all?} | Modify file |
| Glob | {pattern, path?} | Match files |
| Grep | {pattern, path?, glob?, ...flags} | Search files |
| WebFetch | {url, prompt} | Fetch & analyze web page |
| WebSearch | {query, allowed_domains?} | Web search |
| NotebookEdit | {notebook_path, cell_id?, new_source} | Edit Jupyter |
| TodoWrite | {todos: [{content, status}]} | Manage todos |

## Thinking Configuration

```python
class ThinkingConfigAdaptive(TypedDict):
    type: Literal["adaptive"]

class ThinkingConfigEnabled(TypedDict):
    type: Literal["enabled"]
    budget_tokens: int

class ThinkingConfigDisabled(TypedDict):
    type: Literal["disabled"]

ThinkingConfig = ThinkingConfigAdaptive | ThinkingConfigEnabled | ThinkingConfigDisabled
```

## Sandbox Settings

```python
class SandboxSettings(TypedDict, total=False):
    enabled: bool
    autoAllowBashIfSandboxed: bool
    excludedCommands: list[str]
    allowUnsandboxedCommands: bool
    network: SandboxNetworkConfig
    ignoreViolations: SandboxIgnoreViolations
    enableWeakerNestedSandbox: bool
```
