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
def scitex_dir(tmp_path):
    """Point SCITEX_DIR at a temp location for the test, then restore.

    A yield-based env fixture (no monkeypatch) — the package reads
    ``os.environ["SCITEX_DIR"]`` directly, so setting + restoring the
    real env var exercises the real lookup path.
    """
    saved = os.environ.get("SCITEX_DIR")
    os.environ["SCITEX_DIR"] = str(tmp_path)
    try:
        yield tmp_path
    finally:
        if saved is None:
            os.environ.pop("SCITEX_DIR", None)
        else:
            os.environ["SCITEX_DIR"] = saved


@pytest.fixture
def home_no_scitex_dir(tmp_path):
    """Unset SCITEX_DIR and point HOME at tmp_path; restore both after."""
    saved_dir = os.environ.get("SCITEX_DIR")
    saved_home = os.environ.get("HOME")
    os.environ.pop("SCITEX_DIR", None)
    os.environ["HOME"] = str(tmp_path)
    try:
        yield tmp_path
    finally:
        if saved_dir is not None:
            os.environ["SCITEX_DIR"] = saved_dir
        if saved_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = saved_home


class TestPathLayout:
    def test_capture_root_is_under_scitex_dir(self, scitex_dir):
        # Arrange
        from scitex_capture._paths import get_capture_root

        # Act
        root = get_capture_root()
        # Assert
        assert root == scitex_dir / "capture"

    def test_runtime_dir_without_category_resolves_to_runtime(self, scitex_dir):
        # Arrange
        from scitex_capture._paths import get_runtime_dir

        # Act
        runtime = get_runtime_dir()
        # Assert
        assert runtime == scitex_dir / "capture" / "runtime"

    def test_runtime_dir_without_category_is_created(self, scitex_dir):
        # Arrange
        from scitex_capture._paths import get_runtime_dir

        # Act
        runtime = get_runtime_dir()
        # Assert
        assert runtime.is_dir()

    def test_runtime_dir_with_category_resolves_under_runtime(self, scitex_dir):
        # Arrange
        from scitex_capture._paths import get_runtime_dir

        # Act
        custom = get_runtime_dir("custom")
        # Assert
        assert custom == scitex_dir / "capture" / "runtime" / "custom"

    def test_runtime_dir_with_category_is_created(self, scitex_dir):
        # Arrange
        from scitex_capture._paths import get_runtime_dir

        # Act
        custom = get_runtime_dir("custom")
        # Assert
        assert custom.is_dir()

    def test_screenshots_dir_resolves_under_runtime(self, scitex_dir):
        # Arrange
        from scitex_capture._paths import get_screenshots_dir

        # Act
        shots = get_screenshots_dir()
        # Assert
        assert shots == scitex_dir / "capture" / "runtime" / "screenshots"

    def test_screenshots_dir_is_created(self, scitex_dir):
        # Arrange
        from scitex_capture._paths import get_screenshots_dir

        # Act
        shots = get_screenshots_dir()
        # Assert
        assert shots.is_dir()

    def test_gifs_dir_resolves_under_runtime(self, scitex_dir):
        # Arrange
        from scitex_capture._paths import get_gifs_dir

        # Act
        gifs = get_gifs_dir()
        # Assert
        assert gifs == scitex_dir / "capture" / "runtime" / "gifs"

    def test_gifs_dir_is_created(self, scitex_dir):
        # Arrange
        from scitex_capture._paths import get_gifs_dir

        # Act
        gifs = get_gifs_dir()
        # Assert
        assert gifs.is_dir()

    def test_tmp_dir_resolves_under_runtime(self, scitex_dir):
        # Arrange
        from scitex_capture._paths import get_tmp_dir

        # Act
        tmp = get_tmp_dir()
        # Assert
        assert tmp == scitex_dir / "capture" / "runtime" / "tmp"

    def test_tmp_dir_is_created(self, scitex_dir):
        # Arrange
        from scitex_capture._paths import get_tmp_dir

        # Act
        tmp = get_tmp_dir()
        # Assert
        assert tmp.is_dir()

    def test_capture_dir_aliases_screenshots_dir(self, scitex_dir):
        # Arrange
        from scitex_capture._paths import get_capture_dir, get_screenshots_dir

        # Act
        capture_dir = get_capture_dir()
        # Assert
        assert capture_dir == get_screenshots_dir()

    def test_scitex_dir_unset_falls_back_to_home_dotscitex(self, home_no_scitex_dir):
        # Arrange
        from scitex_capture._paths import get_capture_root

        # Act
        root = get_capture_root()
        # Assert
        assert root == home_no_scitex_dir / ".scitex" / "capture"


class TestWritesStayUnderRuntime:
    """Functional pin: every write path lands beneath runtime/."""

    def test_screenshot_worker_default_output_dir_under_runtime(self, scitex_dir):
        # Arrange
        from scitex_capture.capture import ScreenshotWorker

        runtime = scitex_dir / "capture" / "runtime"
        # Act
        worker = ScreenshotWorker()
        # Assert
        assert runtime in worker.output_dir.parents or worker.output_dir == runtime

    def test_start_capture_default_output_dir_under_runtime(self, scitex_dir):
        # Arrange
        from scitex_capture.capture import CaptureManager

        mgr = CaptureManager()
        runtime = scitex_dir / "capture" / "runtime"
        # Act
        worker = mgr.start_capture()
        try:
            resolved = worker.output_dir
        finally:
            mgr.stop_capture()
        # Assert
        assert runtime in resolved.parents or resolved == runtime

    def test_single_screenshot_default_path_under_runtime_screenshots(self, scitex_dir):
        # Arrange
        from scitex_capture.capture import CaptureManager

        screenshots = scitex_dir / "capture" / "runtime" / "screenshots"
        mgr = CaptureManager()
        # Act
        result = mgr.take_single_screenshot()
        # Assert
        # Capture may succeed (display present) or return None (headless);
        # either way the default path must resolve under runtime/screenshots.
        assert result is None or str(screenshots) in str(result)

    def test_single_screenshot_never_writes_to_legacy_tmp_path(self, scitex_dir):
        # Arrange
        from scitex_capture.capture import CaptureManager

        mgr = CaptureManager()
        legacy = Path("/tmp/scitex_capture_screenshots")
        # Act
        mgr.take_single_screenshot()
        # Assert
        assert not legacy.exists()


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
