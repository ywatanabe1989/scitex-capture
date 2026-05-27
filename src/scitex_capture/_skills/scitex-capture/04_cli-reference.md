---
description: |
  [TOPIC] scitex-capture CLI Reference
  [DETAILS] Top-level subcommands of the `scitex-capture` CLI — info, list-windows, monitor (start/stop), gif, mcp, list-python-apis.
tags: [scitex-capture-cli-reference]
---

# CLI Reference

`scitex-capture` is the entry point installed by `pip install scitex-capture`.

## Subcommands

| Command                                    | Purpose                                |
|--------------------------------------------|----------------------------------------|
| `scitex-capture [MESSAGE]`                 | Snap a screenshot (default action)     |
| `scitex-capture --all`                     | Capture all monitors                   |
| `scitex-capture --app <name>`              | Capture a specific app window          |
| `scitex-capture --url <url>`               | Capture a browser page                 |
| `scitex-capture show-info`                 | Show detected monitors, windows, etc.  |
| `scitex-capture list-windows`              | List visible OS windows                |
| `scitex-capture start-monitor`             | Start continuous capture loop          |
| `scitex-capture stop-monitor`              | Stop the running capture loop          |
| `scitex-capture make-gif`                  | Assemble latest session frames into GIF|
| `scitex-capture mcp start`                 | Start MCP server (stdio) for AI agents |
| `scitex-capture mcp list-tools`            | List exposed MCP tools                 |
| `scitex-capture list-python-apis`          | Inventory the Python API surface       |
| `scitex-capture skills list`               | List bundled skill files               |
| `scitex-capture skills get <name>`         | Print one bundled skill                |
| `scitex-capture skills install`            | Copy skills to `~/.claude/skills/`     |

Most commands accept `--as-json` for machine-readable output and `--yes` /
`--dry-run` where actions are destructive.

## Examples

```bash
scitex-capture show-info --as-json
scitex-capture start-monitor --interval 10
scitex-capture stop-monitor --yes
scitex-capture make-gif
scitex-capture "debug message" --all        # snap with message, all monitors
scitex-capture mcp start                    # speak MCP/stdio for an AI agent
```
