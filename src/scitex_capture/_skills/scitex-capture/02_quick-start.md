---
description: |
  [TOPIC] Quick start
  [DETAILS] Single capture, monitor loop, and animated GIF — three calls cover most agent screenshot needs.
tags: [scitex-capture-quick-start]
---

# Quick Start

## Single screenshot

```python
from scitex_capture import capture

path = capture(monitor=0, output_path="/tmp/screen.jpg")
print(path)
```

`monitor=0` is the primary display; `monitor=-1` means "all monitors".

## Continuous monitor loop

```python
from scitex_capture import start_monitor, stop_monitor

start_monitor(interval=10, duration=300)     # snapshot every 10s for 5 min
# ... do work ...
stop_monitor()
```

Frames land under `$SCITEX_DIR/capture/<session>/`.

## Animated GIF

```python
from scitex_capture import gif

gif("/tmp/capture/session_xyz", output="/tmp/timelapse.gif", fps=4)
```

## CLI

```bash
scitex-capture info
scitex-capture monitor start --interval 10 --monitor 0
scitex-capture monitor stop
scitex-capture gif
```

## Next

- [03_python-api.md](03_python-api.md) — full surface
- [04_cli-reference.md](04_cli-reference.md) — all CLI subcommands
