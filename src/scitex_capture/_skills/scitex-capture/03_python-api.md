---
description: |
  [TOPIC] Python API
  [DETAILS] Public callables — capture, start_monitor / stop_monitor, capture_window, get_info, gif helpers, session.
tags: [scitex-capture-python-api]
---

# Python API

## Imports

```python
from scitex_capture import (
    capture,
    capture_window,
    start_monitor,
    stop_monitor,
    get_info,
    session,
    gif,
)
```

## Single-frame capture

| Callable                                | Purpose                                  |
|-----------------------------------------|------------------------------------------|
| `capture(monitor=0, output_path=None)`  | One screenshot to disk; returns path     |
| `capture_window(window_handle, output_path=None)` | Capture a specific OS window   |
| `get_info()`                            | Dict of monitors, JPEG quality, paths    |

## Monitoring loop

```python
start_monitor(interval=10, duration=300, monitor=0)
# ... runs in background thread ...
stop_monitor()
```

Frames are written to `$SCITEX_DIR/capture/runtime/screenshots/<session_id>_*.jpg`
(falls back to `~/.scitex/capture/runtime/screenshots/...`). The
package root `$SCITEX_DIR/capture/` is reserved for tracked
declarative inputs — runtime artefacts always live under
`runtime/<category>/`.

## Sessions

```python
with session(name="experiment") as s:
    s.capture()                               # snapshots into the session dir
    # work happens inside the with-block
```

## GIF assembly

```python
from scitex_capture import gif

gif(input_dir, output="timelapse.gif", fps=4)
```

See `gif.*` submodule for additional encoders (mp4, webp).

## Output paths

All artefacts default to `$SCITEX_DIR/capture/runtime/<category>/`
(screenshots → `runtime/screenshots/`, GIFs → `runtime/gifs/`,
scratch temp → `runtime/tmp/`). Override with `output_path=` /
`output_dir=` on individual calls, or relocate the whole tree with
`SCITEX_DIR` at the env level.
