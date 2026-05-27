---
description: |
  [TOPIC] Quick start
  [DETAILS] Single capture, monitor loop, and animated GIF — three calls cover most agent screenshot needs.
tags: [scitex-capture-quick-start]
---

# Quick Start

## Single screenshot

```python
from scitex_capture import snap

path = snap("debug message")
print(path)

# All monitors, custom quality
path = snap(capture_all=True, quality=85)
```

## Continuous monitor loop

```python
from scitex_capture import start, stop

start(interval=10)        # snapshot every 10s
# ... do work ...
stop()
```

Frames land under `$SCITEX_DIR/capture/runtime/screenshots/`.

## Animated GIF

```python
from scitex_capture import gif

path = gif()  # GIF from the latest monitoring session
```

## CLI

```bash
scitex-capture show-info
scitex-capture start-monitor --interval 10
scitex-capture stop-monitor
scitex-capture make-gif
```

## Next

- [03_python-api.md](03_python-api.md) — full surface
- [04_cli-reference.md](04_cli-reference.md) — all CLI subcommands
