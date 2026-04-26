# scitex-capture

Session-based screen capture extracted from the [SciTeX](https://github.com/ywatanabe1989/scitex-python) ecosystem as a standalone package.

Single screenshots, multi-frame session capture → animated GIFs, grid overlays, monitor + cursor info, optional MCP server, optional Playwright integration. Optimised for WSL→Windows-host capture and for AI agents that need a "what does my screen look like right now" tool.

## Install

```bash
pip install scitex-capture
pip install "scitex-capture[mcp]"          # + MCP server
pip install "scitex-capture[playwright]"   # + browser capture
pip install "scitex-capture[all]"          # everything
```

## Usage

```python
import scitex_capture as cap

# One-shot screenshot
path = cap.snap("debug message")
path = cap.snap(capture_all=True)

# Inspect monitors / windows
info = cap.get_info()

# Continuous session capture
session_id = cap.start(interval=2)
# ... do work ...
cap.stop(session_id)
gif_path = cap.gif(session_id)

# Latest session
gif = cap.create_gif_from_latest_session()
```

CLI: `scitex-capture --help`.

## Status

Standalone fork of `scitex.capture`. Only deps are Pillow + mss (with
playwright + mcp as opt-ins). The umbrella package's `scitex.capture`
import path is preserved via a `sys.modules`-alias bridge. 146/146 tests pass.

## License

AGPL-3.0-only (see [LICENSE](./LICENSE)).
