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
    snap,
    capture_window,
    start,
    stop,
    get_info,
    session,
    gif,
    make_gif,
)
```

## Single-frame capture

| Callable                                                  | Purpose                                  |
|-----------------------------------------------------------|------------------------------------------|
| `snap(message=None, path=None, quality=85, ...)`          | One screenshot to disk; returns path     |
| `capture_window(window_handle, output_path=None)`         | Capture a specific OS window             |
| `get_info()`                                              | Dict of monitors, windows, desktops      |

Notes:
- `snap()` writes JPEG files to `$SCITEX_DIR/capture/runtime/screenshots/`
- Use `path=` or `output_dir=` to override the destination
- For all monitors, pass `capture_all=True`

## Monitoring loop

```python
start(interval=10, monitor_id=0)
# ... runs in background thread ...
stop()
```

Frames are written to `$SCITEX_DIR/capture/runtime/screenshots/<session_id>_*.jpg`
(falls back to `~/.scitex/capture/runtime/screenshots/...`). The
package root `$SCITEX_DIR/capture/` is reserved for tracked
declarative inputs — runtime artefacts always live under
`runtime/<category>/`.

## Sessions

```python
from scitex_capture import session

with session(interval=2) as s:
    # screenshots are captured every 2s inside the with-block
    import time
    time.sleep(10)
```

Frames land under `$SCITEX_DIR/capture/runtime/screenshots/`.

## GIF assembly

```python
from scitex_capture import gif, make_gif, create_gif_from_files

# Latest monitoring session
path = gif()
path = make_gif()

# Specific session or files
path = create_gif_from_files(["frame1.jpg", "frame2.jpg"], "output.gif")
```

GIFs are written to `$SCITEX_DIR/capture/runtime/gifs/`.

## Output paths

All artefacts default to `$SCITEX_DIR/capture/runtime/<category>/`
(screenshots → `runtime/screenshots/`, GIFs → `runtime/gifs/`,
scratch temp → `runtime/tmp/`). Override with `output_path=` /
`output_dir=` on individual calls, or relocate the whole tree with
`SCITEX_DIR` at the env level.
