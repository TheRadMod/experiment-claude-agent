# Hosting & Deployment Guide

Source: https://platform.claude.com/docs/en/agent-sdk/hosting
Fetched: 2026-03-25

## System Requirements

- Python 3.10+ (for Python SDK)
- Node.js (required by Claude Code CLI)
- Claude Code CLI: npm install -g @anthropic-ai/claude-code
- Recommended: 1GiB RAM, 5GiB disk, 1 CPU
- Network: Outbound HTTPS to api.anthropic.com

## Deployment Patterns

### Pattern 1: Ephemeral Sessions
New container per task, destroyed on completion.
Use for: bug fixes, invoice processing, translation, image processing.

### Pattern 2: Long-Running Sessions
Persistent containers, multiple agent processes.
Use for: email agents, site builders, high-frequency chat bots.

### Pattern 3: Hybrid Sessions
Ephemeral containers hydrated with history/state.
Use for: project management, deep research, customer support.

### Pattern 4: Single Containers
Multiple agent processes in one global container.
Use for: simulations, closely collaborating agents.

## Sandbox Providers

- Modal Sandbox
- Cloudflare Sandboxes
- Daytona
- E2B
- Fly Machines
- Vercel Sandbox

## Sandbox Settings (Programmatic)

```python
sandbox_settings: SandboxSettings = {
    "enabled": True,
    "autoAllowBashIfSandboxed": True,
    "network": {"allowLocalBinding": True},
}
options = ClaudeAgentOptions(sandbox=sandbox_settings)
```

## Key Notes

- Dominant cost is API tokens, not container hosting (~5 cents/hour)
- Agent sessions don't timeout, but use maxTurns to prevent loops
- Same logging infrastructure works for containers
