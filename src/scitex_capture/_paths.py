#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_capture/_paths.py
# ----------------------------------------
"""Canonical filesystem layout for scitex-capture local state.

Everything that scitex-capture writes lives under
``$SCITEX_DIR/capture/runtime/<category>/`` (defaults to
``~/.scitex/capture/runtime/<category>/``). The package root
``$SCITEX_DIR/capture/`` itself is reserved for tracked declarative
inputs that the operator's dotfiles repo commits — see
``scitex_dev._skills.general.01_ecosystem_06_local-state-directories``.

Public helpers below return the *logical* directory each consumer
asks for (e.g. ``get_capture_dir()`` still means "where screenshots
go"); only the on-disk layout — namely the extra ``runtime/<cat>/``
segment — changed.
"""
from __future__ import annotations

import os
from pathlib import Path

__all__ = [
    "get_capture_root",
    "get_runtime_dir",
    "get_capture_dir",
    "get_screenshots_dir",
    "get_gifs_dir",
    "get_tmp_dir",
]


# Categories carved out under runtime/. Keep this list narrow and
# deliberate; each value is a directory name under runtime/.
_SCREENSHOTS = "screenshots"
_GIFS = "gifs"
_TMP = "tmp"


def _scitex_base() -> Path:
    """Return ``$SCITEX_DIR`` if set, otherwise ``~/.scitex``."""
    return Path(os.environ.get("SCITEX_DIR", str(Path.home() / ".scitex")))


def get_capture_root() -> Path:
    """Return the scitex-capture package root, ``$SCITEX_DIR/capture``.

    The root itself is reserved for tracked inputs (config.yaml,
    etc.). All writes must go through ``get_runtime_dir(...)``.
    """
    return _scitex_base() / "capture"


def get_runtime_dir(category: str | None = None) -> Path:
    """Return ``$SCITEX_DIR/capture/runtime[/<category>]``.

    The directory is created on demand so callers don't have to
    ``mkdir`` themselves (lazy mkdir is the package convention; see
    the local-state-directories skill §3.5).
    """
    runtime = get_capture_root() / "runtime"
    target = runtime if category is None else runtime / category
    target.mkdir(parents=True, exist_ok=True)
    return target


def get_capture_dir() -> Path:
    """Return the directory screenshots are written to.

    Logical name preserved for back-compat with the MCP server and
    handler code that previously returned ``~/.scitex/capture`` —
    the on-disk layout moved to ``runtime/screenshots/``.
    """
    return get_screenshots_dir()


def get_screenshots_dir() -> Path:
    """Return ``runtime/screenshots/`` — single shots and monitor frames."""
    return get_runtime_dir(_SCREENSHOTS)


def get_gifs_dir() -> Path:
    """Return ``runtime/gifs/`` — assembled animated outputs."""
    return get_runtime_dir(_GIFS)


def get_tmp_dir() -> Path:
    """Return ``runtime/tmp/`` — replaces ``/tmp/scitex_capture_*``.

    The local-state-directories skill §5 forbids ``/tmp/scitex-<pkg>-*``
    paths because they fragment the layout and break ``SCITEX_DIR``
    relocation.
    """
    return get_runtime_dir(_TMP)


# EOF
