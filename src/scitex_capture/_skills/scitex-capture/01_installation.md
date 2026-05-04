---
description: |
  [TOPIC] Installation
  [DETAILS] pip install scitex-capture. Uses `mss` for cross-platform screen grabs; on WSL, screenshots reach Windows monitors through the WSLg display.
tags: [scitex-capture-installation]
---

# Installation

## Standard

```bash
pip install scitex-capture
```

Pulls `mss` (multi-monitor screen grab), `Pillow` (JPEG encoding), and `click`
(CLI). On WSL, requires WSLg (default on WSL2 since 2022).

## Verify

```bash
scitex-capture --version
scitex-capture info                          # detected monitors + JPEG settings
python -c "import scitex_capture; print(scitex_capture.__version__)"
python -c "from scitex_capture import capture; capture(monitor=0, output_path='/tmp/test.jpg')"
```

## Editable install (development)

```bash
git clone https://github.com/ywatanabe1989/scitex-capture
cd scitex-capture
pip install -e .
```

## Platform notes

- **WSL/Windows**: works out of the box via WSLg.
- **macOS**: grant Screen Recording permission to your terminal.
- **Linux/X11**: works via `mss`; on Wayland, behavior depends on compositor.
