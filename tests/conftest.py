"""Pytest fixtures and rootdir marker for this package.

An empty conftest.py at tests/ is the canonical SciTeX
convention (audit-project PS208) — it pins the pytest
rootdir and gives downstream fixtures a home.

This module also wires subprocess-coverage at import time so child
Python interpreters spawned during tests (subprocess.run,
jupyter nbconvert --execute, pytest-xdist workers) contribute to
the coverage report instead of being silently dropped. The fix has
three parts (see scitex-dev skill leaf
``05_development_06_subprocess-coverage.md``):

1. ``[tool.coverage.run] parallel = true`` in ``pyproject.toml``
   (so every child writes its own shard rather than racing).
2. ``COVERAGE_PROCESS_START`` + ``COVERAGE_FILE`` force-set here
   at module-import time (``os.environ.setdefault`` is a silent
   no-op because pytest-cov has already set ``COVERAGE_FILE`` to a
   tmp dir by the time ``conftest.py`` runs).
3. An idempotent ``.pth`` shim in ``site-packages`` that calls
   ``coverage.process_startup()`` on every Python interpreter.
"""

from __future__ import annotations

import os
import sysconfig
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Force-set (NOT setdefault — pytest-cov has already set these).
os.environ["COVERAGE_PROCESS_START"] = str(_PROJECT_ROOT / "pyproject.toml")
os.environ["COVERAGE_FILE"] = str(_PROJECT_ROOT / ".coverage")


def _ensure_subprocess_coverage_shim() -> None:
    """Drop an idempotent ``.pth`` file in site-packages that
    auto-starts coverage in every child Python interpreter via
    ``coverage.process_startup()``.
    """
    purelib = Path(sysconfig.get_paths()["purelib"])
    pth = purelib / "_scitex_capture_subprocess_coverage.pth"
    shim = (
        "import os, coverage\n"
        "if os.environ.get('COVERAGE_PROCESS_START'):\n"
        "    coverage.process_startup()\n"
    )
    try:
        if not pth.exists() or pth.read_text() != shim:
            pth.write_text(shim)
    except OSError:
        # site-packages may be read-only (e.g. system Python);
        # silently skip — local dev venvs are writable and that's
        # where this matters.
        pass


_ensure_subprocess_coverage_shim()
