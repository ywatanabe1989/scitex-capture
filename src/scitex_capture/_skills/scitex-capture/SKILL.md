---
name: scitex-capture
description: |
  [WHAT] AI's camera — screen capture optimized for WSL/Windows.
  [WHEN] `capture(monitor=0)` grabs a single screenshot; `monitor(interval=10, duration=300)` runs a continuous capture loop.
  [HOW] JPEG-compressed, multi-monitor aware. Drop-in replacement for `subprocess.run(['screencapture', ...])` shells out and `pyautogui.screenshot()` calls that silently fail on WSL.
tags: [scitex-capture]
primary_interface: python
interfaces:
  python: 3
  cli: 1
  mcp: 0
  skills: 2
  http: 0
---

> **Interfaces:** Python ⭐⭐⭐ · CLI ⭐ · MCP — · Skills ⭐⭐ · Hook — · HTTP —

# scitex-capture

AI's camera — screen capture optimized for WSL/Windows. `capture(monitor=0)` grabs a single screenshot; `monitor(interval=10, duration=300)` runs a continuous capture loop. JPEG-compressed, multi-monitor aware. Drop-in replacement for `subprocess.run(['screencapture', ...])` shells out and `pyautogui.screenshot()` calls that silently fail on WSL.

See README.md and the package's public `__init__.py` for the full
function list. This skill leaf exists so agents discover the package
exists and roughly what shape it has — refer to the source for
signatures.
