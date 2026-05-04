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
| `scitex-capture info`                      | Show detected monitors, JPEG settings  |
| `scitex-capture list-windows`              | List visible OS windows                |
| `scitex-capture monitor start`             | Start continuous capture loop          |
| `scitex-capture monitor stop`              | Stop the running capture loop          |
| `scitex-capture gif`                       | Assemble session frames into a GIF     |
| `scitex-capture mcp start`                 | Start MCP server (stdio) for AI agents |
| `scitex-capture mcp list-tools`            | List exposed MCP tools                 |
| `scitex-capture list-python-apis`          | Inventory the Python API surface       |

Most commands accept `--as-json` for machine-readable output and `--yes` /
`--dry-run` where actions are destructive.

## Examples

```bash
scitex-capture info --as-json
scitex-capture monitor start --interval 10 --monitor 0
scitex-capture monitor stop --yes
scitex-capture gif
scitex-capture mcp start                    # speak MCP/stdio for an AI agent
```
