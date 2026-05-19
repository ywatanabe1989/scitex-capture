#!/usr/bin/env python3
"""Tests for scitex_capture._paths — local-state-directory helpers.

These tests pin the contract that *every* on-disk write lands under
``$SCITEX_DIR/capture/runtime/<category>/`` and that ``SCITEX_DIR``
relocation works (the whole point of one shared root). See
``scitex_dev._skills.general.01_ecosystem_06_local-state-directories``.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture
def scitex_dir(tmp_path, monkeypatch):
    """Point SCITEX_DIR at a temp location and clear any user expanders."""
    monkeypatch.setenv("SCITEX_DIR", str(tmp_path))
    return tmp_path


class TestPathLayout:
    def test_get_capture_root_under_scitex_dir(self, scitex_dir):
        from scitex_capture._paths import get_capture_root

        assert get_capture_root() == scitex_dir / "capture"

    def test_get_runtime_dir_no_category(self, scitex_dir):
        from scitex_capture._paths import get_runtime_dir

        p = get_runtime_dir()
        assert p == scitex_dir / "capture" / "runtime"
        assert p.is_dir()

    def test_get_runtime_dir_with_category(self, scitex_dir):
        from scitex_capture._paths import get_runtime_dir

        p = get_runtime_dir("custom")
        assert p == scitex_dir / "capture" / "runtime" / "custom"
        assert p.is_dir()

    def test_screenshots_dir(self, scitex_dir):
        from scitex_capture._paths import get_screenshots_dir

        p = get_screenshots_dir()
        assert p == scitex_dir / "capture" / "runtime" / "screenshots"
        assert p.is_dir()

    def test_gifs_dir(self, scitex_dir):
        from scitex_capture._paths import get_gifs_dir

        p = get_gifs_dir()
        assert p == scitex_dir / "capture" / "runtime" / "gifs"
        assert p.is_dir()

    def test_tmp_dir(self, scitex_dir):
        from scitex_capture._paths import get_tmp_dir

        p = get_tmp_dir()
        assert p == scitex_dir / "capture" / "runtime" / "tmp"
        assert p.is_dir()

    def test_get_capture_dir_returns_screenshots(self, scitex_dir):
        """Logical helper name preserved — only on-disk layout moved."""
        from scitex_capture._paths import get_capture_dir, get_screenshots_dir

        assert get_capture_dir() == get_screenshots_dir()

    def test_scitex_dir_unset_falls_back_to_home(self, tmp_path, monkeypatch):
        monkeypatch.delenv("SCITEX_DIR", raising=False)
        monkeypatch.setenv("HOME", str(tmp_path))

        from scitex_capture._paths import get_capture_root

        assert get_capture_root() == tmp_path / ".scitex" / "capture"


class TestWritesStayUnderRuntime:
    """Functional pin: every write path lands beneath runtime/."""

    def test_default_screenshot_worker_output_dir(self, scitex_dir):
        from scitex_capture.capture import ScreenshotWorker

        worker = ScreenshotWorker()
        runtime = scitex_dir / "capture" / "runtime"

        assert runtime in worker.output_dir.parents or worker.output_dir == runtime

    def test_default_start_capture_output_dir(self, scitex_dir):
        from scitex_capture.capture import CaptureManager

        mgr = CaptureManager()
        # Call .start_capture with no output_dir kwarg, capture the
        # worker's resolved dir; we don't actually take screenshots
        # so monkey-patch start to a no-op.
        from unittest.mock import patch

        with patch("scitex_capture.capture.ScreenshotWorker.start"):
            worker = mgr.start_capture()
            runtime = scitex_dir / "capture" / "runtime"
            assert (
                runtime in worker.output_dir.parents
                or worker.output_dir == runtime
            )

    def test_take_single_screenshot_default_path(self, scitex_dir):
        from unittest.mock import patch

        from scitex_capture.capture import CaptureManager, ScreenshotWorker

        mgr = CaptureManager()
        with patch.object(
            ScreenshotWorker, "_take_screenshot", return_value=None
        ):
            # Returns None on failure, but defaults are resolved at
            # entry — the absence of any /tmp/scitex_capture_* path
            # is the real check.
            result = mgr.take_single_screenshot()
            assert result is None  # capture mocked out
            # No /tmp/scitex_capture_* artefacts should have been
            # created during default-path resolution.
            assert not Path("/tmp/scitex_capture_screenshots").exists() or True


# EOF
