# scitex-capture

<!-- scitex-badges:start -->
[![PyPI](https://img.shields.io/pypi/v/scitex-capture.svg)](https://pypi.org/project/scitex-capture/)
[![Python](https://img.shields.io/pypi/pyversions/scitex-capture.svg)](https://pypi.org/project/scitex-capture/)
[![Tests](https://github.com/ywatanabe1989/scitex-capture/actions/workflows/test.yml/badge.svg)](https://github.com/ywatanabe1989/scitex-capture/actions/workflows/test.yml)
[![Install Test](https://github.com/ywatanabe1989/scitex-capture/actions/workflows/install-test.yml/badge.svg)](https://github.com/ywatanabe1989/scitex-capture/actions/workflows/install-test.yml)
[![Coverage](https://codecov.io/gh/ywatanabe1989/scitex-capture/graph/badge.svg)](https://codecov.io/gh/ywatanabe1989/scitex-capture)
[![Docs](https://readthedocs.org/projects/scitex-capture/badge/?version=latest)](https://scitex-capture.readthedocs.io/en/latest/)
[![License: AGPL v3](https://img.shields.io/badge/license-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
<!-- scitex-badges:end -->

<p align="center">
  <a href="https://scitex.ai">
    <img src="docs/scitex-logo-blue-cropped.png" alt="SciTeX" width="400">
  </a>
</p>

<p align="center"><b>Session-based screen capture — single screenshots, multi-frame sessions → animated GIFs, grid overlays, monitor + cursor info. Optimised for WSL→Windows host and for AI agents that need a "what does my screen look like right now" tool.</b></p>

<p align="center">
  <a href="https://scitex-capture.readthedocs.io/">Full Documentation</a> · <code>pip install scitex-capture</code>
</p>

---

## Installation

```bash
pip install scitex-capture
pip install "scitex-capture[mcp]"          # + MCP server
pip install "scitex-capture[playwright]"   # + browser capture
pip install "scitex-capture[all]"          # everything
```

## 2 Interfaces

<details open>
<summary><strong>Python API</strong></summary>

<br>

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

</details>

<details>
<summary><strong>CLI</strong></summary>

<br>

```bash
scitex-capture --help
scitex-capture snap "debug message"
scitex-capture start --interval 2
scitex-capture stop <session-id>
scitex-capture gif <session-id>
```

</details>

## Status

Standalone fork of `scitex.capture`. Only deps are Pillow + mss (with
playwright + mcp as opt-ins). The umbrella package's `scitex.capture`
import path is preserved via a `sys.modules`-alias bridge. 146/146 tests pass.

## Part of SciTeX

`scitex-capture` is part of [**SciTeX**](https://scitex.ai). Install via
the umbrella with `pip install scitex[capture]` to use as
`scitex.capture` (Python) or `scitex capture ...` (CLI).

>Four Freedoms for Research
>
>0. The freedom to **run** your research anywhere — your machine, your terms.
>1. The freedom to **study** how every step works — from raw data to final manuscript.
>2. The freedom to **redistribute** your workflows, not just your papers.
>3. The freedom to **modify** any module and share improvements with the community.
>
>AGPL-3.0 — because we believe research infrastructure deserves the same freedoms as the software it runs on.

## License

AGPL-3.0-only (see [LICENSE](./LICENSE)).

---

<p align="center">
  <a href="https://scitex.ai" target="_blank"><img src="docs/scitex-icon-navy-inverted.png" alt="SciTeX" width="40"/></a>
</p>
