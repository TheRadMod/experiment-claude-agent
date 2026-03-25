# Claude Agent SDK - Experimental Project

## Overview

This experiment explores the Claude Agent SDK (formerly Claude Code SDK) — Anthropic's
Python library that exposes the same tools, agent loop, and context management that power
Claude Code, as a programmable SDK. The goal is to build modular, self-contained scripts
that demonstrate each major capability of the SDK, creating a reusable reference library
for building larger agent-based applications.

## Technology Version

- Technology: Claude Agent SDK
- Package: `claude-agent-sdk`
- Version: 0.1.50
- Python requirement: >= 3.10
- Version check date: 2026-03-25
- PyPI: https://pypi.org/project/claude-agent-sdk/
- Note: Future sessions should check if a newer version is available
  and decide whether to use this version or upgrade.

## Documentation Sources

IMPORTANT: All scripts in this experiment MUST be based on the fetched
documentation stored in the docs/ folder, NOT on general training knowledge.
This ensures accuracy for the specific version.

- Official docs URL: https://platform.claude.com/docs/en/agent-sdk/overview
- Quickstart: https://platform.claude.com/docs/en/agent-sdk/quickstart
- Python API reference: https://platform.claude.com/docs/en/agent-sdk/python
- Hooks guide: https://platform.claude.com/docs/en/agent-sdk/hooks
- Sessions guide: https://platform.claude.com/docs/en/agent-sdk/sessions
- MCP guide: https://platform.claude.com/docs/en/agent-sdk/mcp
- Subagents guide: https://platform.claude.com/docs/en/agent-sdk/subagents
- Permissions guide: https://platform.claude.com/docs/en/agent-sdk/permissions
- Hosting guide: https://platform.claude.com/docs/en/agent-sdk/hosting
- GitHub repo: https://github.com/anthropics/claude-agent-sdk-python
- Demo apps: https://github.com/anthropics/claude-agent-sdk-demos

- docs/ folder contents:
  - 01_overview.md — SDK overview and capabilities summary
  - 02_quickstart.md — Setup, installation, first agent
  - 03_python_api_reference.md — Complete Python API (functions, classes, types)
  - 04_hooks.md — Hook system (PreToolUse, PostToolUse, etc.)
  - 05_sessions.md — Session management (resume, fork, continue)
  - 06_mcp.md — MCP server integration (stdio, HTTP, in-process)
  - 07_subagents.md — Multi-agent orchestration
  - 08_permissions.md — Permission modes and tool access control
  - 09_hosting.md — Deployment patterns and sandbox settings
  - 10_demos.md — Official demo application descriptions

## Key Concepts

1. **Agentic loop** — The async iterator pattern (query/receive) where Claude autonomously
   reads files, runs commands, and makes decisions across multiple turns
2. **Built-in tools** — Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch —
   tools that execute without you implementing them
3. **Custom tools via MCP** — Define Python functions as tools using @tool decorator
   and create_sdk_mcp_server(), running in-process without subprocess overhead
4. **Hooks** — Callback functions that intercept agent behavior at key lifecycle points
   (PreToolUse, PostToolUse, Stop, etc.) to block, modify, audit, or log actions
5. **Sessions** — Persistent conversation histories that can be resumed, forked, or
   continued across multiple exchanges
6. **Subagents** — Isolated agent instances with their own context, tools, and prompts
   that can run in parallel for focused subtasks
7. **Permission system** — Fine-grained control via modes (acceptEdits, bypassPermissions,
   plan) and rules (allowed_tools, disallowed_tools, canUseTool callbacks)

## Capabilities to Explore

1. Basic query() — simple one-shot agent interaction
2. Message types — parsing AssistantMessage, ResultMessage, SystemMessage, StreamEvent
3. ClaudeSDKClient — multi-turn continuous conversations
4. Built-in tools — using Read, Edit, Bash, Glob, Grep with tool control
5. System prompts — customizing agent behavior with system_prompt
6. Custom tools via @tool decorator and in-process MCP servers
7. External MCP servers — connecting stdio and HTTP/SSE MCP servers
8. Hooks — PreToolUse (block/modify), PostToolUse (log/audit), Stop, Notification
9. Permission modes — acceptEdits, bypassPermissions, plan, canUseTool callbacks
10. Sessions — resume, fork, continue_conversation, list_sessions
11. Subagents — multi-agent orchestration with AgentDefinition
12. Streaming input — AsyncIterable prompt for streaming data to agent
13. Interrupts — interrupting a running agent mid-task
14. Error handling — CLINotFoundError, ProcessError, CLIJSONDecodeError
15. Structured output — output_format with JSON schema
16. Budget and turn limits — max_turns, max_budget_usd
17. Thinking configuration — adaptive, enabled (with budget_tokens), disabled
18. Sandbox settings — programmatic sandboxing for security
19. Multi-agent pipeline — chaining subagents into a coordinated workflow
20. Production patterns — hosting, deployment, cost tracking

## Script Conventions

- Language: Python
- Naming: NN_descriptive_name.py (numbered for progression)
- Each script: Self-contained, independently runnable with `python3 NN_name.py`
- Logging: `logging` module with console output (StreamHandler)
- Output: Both terminal output and file output (where applicable, e.g., logs, reports)
- run_all script: Yes — `run_all.py` with selective options (pick scripts to run)
- Docstring: Each script starts with a module docstring explaining the concept
- Main guard: All scripts use `if __name__ == "__main__"`
- Async: All scripts use `asyncio.run(main())` pattern
- Environment: ANTHROPIC_API_KEY must be set as environment variable
- Descriptive variable names throughout
- Function/class descriptions at top of each definition

## Progression Plan

### Phase 1: Foundations
1. `01_basic_query.py` — Simplest query() call, print response
2. `02_message_types.py` — Parse and display all message types (Assistant, Result, System, etc.)
3. `03_built_in_tools.py` — Use Read, Glob, Grep tools to analyze a codebase
4. `04_system_prompt.py` — Customize agent behavior with system_prompt

### Phase 2: Interactive & Stateful
5. `05_client_multiturn.py` — ClaudeSDKClient for multi-turn conversations
6. `06_streaming_input.py` — Stream data to agent via AsyncIterable prompt
7. `07_interrupts.py` — Interrupt a running agent mid-task

### Phase 3: Custom Tools
8. `08_custom_tool_basic.py` — Define a tool with @tool decorator
9. `09_sdk_mcp_server.py` — Create in-process MCP server with multiple tools
10. `10_external_mcp.py` — Connect to external stdio/HTTP MCP servers

### Phase 4: Control & Safety
11. `11_hooks_pretooluse.py` — Block/modify tool calls with PreToolUse hooks
12. `12_hooks_posttooluse.py` — Audit/log tool results with PostToolUse hooks
13. `13_hooks_notification.py` — Forward agent notifications to external service
14. `14_permission_modes.py` — Compare acceptEdits, bypassPermissions, plan modes
15. `15_can_use_tool.py` — Custom canUseTool callback for interactive approval

### Phase 5: Sessions & Agents
16. `16_session_resume.py` — Capture session ID, resume a conversation
17. `17_session_fork.py` — Fork a session to explore alternatives
18. `18_subagent_basic.py` — Define and invoke a subagent
19. `19_multi_agent_pipeline.py` — Coordinate multiple subagents for complex tasks

### Phase 6: Advanced & Production
20. `20_error_handling.py` — Handle SDK errors gracefully
21. `21_structured_output.py` — Get JSON-structured responses with output_format
22. `22_budget_limits.py` — Set max_turns and max_budget_usd
23. `23_thinking_config.py` — Control extended thinking behavior
24. `24_sandbox_settings.py` — Programmatic sandbox for secure execution
25. `25_production_agent.py` — Complete production-ready agent with all features

## Prerequisites

- Python 3.10+
- Anthropic API key (set as ANTHROPIC_API_KEY environment variable)
- Install packages:
  ```bash
  cd /home/radmod/pythonprojects/experiments/claude-agent-sdk
  pip install -r requirements.txt
  ```
- Verify setup:
  ```bash
  python3 -c "from claude_agent_sdk import query; print('SDK imported successfully')"
  ```

## Integration Notes

- The `query()` pattern from scripts 01-04 can be extracted as a reusable
  `run_agent()` utility for any project needing one-shot agent execution
- The ClaudeSDKClient pattern from script 05 forms the backbone of any
  interactive chat application or multi-turn workflow
- Custom tools from scripts 08-09 can be packaged as standalone MCP servers
  for any Claude-powered application
- Hook patterns from scripts 11-13 provide reusable audit, security, and
  notification infrastructure for production agents
- The permission system from scripts 14-15 provides template patterns for
  building agents with appropriate safety controls
- The multi-agent pipeline from script 19 demonstrates how to decompose
  complex tasks into coordinated subtasks — applicable to CI/CD, research,
  and code review automation
- Script 25 synthesizes all concepts into a production-ready template

## GitHub Repository
- Repository: https://github.com/TheRadMod/experiment-claude-agent-sdk
- Visibility: public

## Status
- Created: 2026-03-25
- Status: Learning
