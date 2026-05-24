#!/usr/bin/env python3
"""Tests for scitex_capture.utils module.

Tests utility functions for screen capture:
- capture() function (main API)
- take_screenshot() simple interface
- start_monitor()/stop_monitor() for continuous capture
- Cache management
- Category detection

No mocking library is used. Cases that need a *deterministically
failed* screen capture (so the result is None regardless of whether a
display is present) run in a real subprocess that arranges its own
``os.uname`` to report non-WSL and blocks the native backend (``mss``
import fails, ``PATH`` has no ``scrot``) — the real capture path runs
and genuinely cannot succeed. Optional-dependency-absent branches
(playwright, PIL) are exercised the same way: a stub package on
``PYTHONPATH`` raises ImportError so the real except-branch runs.
"""

import os
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path

import pytest


# --------------------------------------------------------------------------
# Real-subprocess helpers — no mock library, genuinely isolated processes.
# --------------------------------------------------------------------------
def _run_capture_subprocess(tmp_path, body, *, blocked_modules=()):
    """Run ``body`` in a child that cannot capture a real screen.

    The child sets a non-WSL ``os.uname``, empties ``PATH`` (no
    ``scrot``), and front-loads stub packages that raise ImportError for
    every name in ``blocked_modules``. ``body`` must print a line the
    caller asserts on. Returns the child's stdout.
    """
    stub_root = tmp_path / "stubs"
    stub_root.mkdir(exist_ok=True)
    for mod in ("mss", *blocked_modules):
        top = mod.split(".")[0]
        (stub_root / f"{top}.py").write_text(
            f'raise ImportError("{top} blocked for test")\n'
        )
    script = tmp_path / "child.py"
    script.write_text(
        "import os, sys, types, tempfile\n"
        'os.uname = lambda: types.SimpleNamespace(release="5.15.0-generic")\n'
        'sys.platform = "linux"\n'
        'os.environ["PATH"] = ""\n' + textwrap.dedent(body)
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(stub_root), env.get("PYTHONPATH", "")])
    proc = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        env=env,
        timeout=40,
    )
    return proc.stdout


class TestCaptureReturnsNoneOnFailure:
    """capture() returns None when the underlying screen grab fails."""

    @pytest.mark.parametrize(
        "kwargs_repr",
        [
            "dict(verbose=False, auto_categorize=False)",
            'dict(message="test message", verbose=False)',
            "dict(monitor_id=1, verbose=False)",
            "dict(capture_all=True, verbose=False)",
            "dict(all=True, verbose=False)",
        ],
        ids=["plain", "message", "monitor_id", "capture_all", "all_shorthand"],
    )
    def test_capture_returns_none_for_each_param_set(self, tmp_path, kwargs_repr):
        # Arrange
        body = f"""
            from scitex_capture.utils import capture
            with tempfile.TemporaryDirectory() as d:
                r = capture(path=os.path.join(d, "t.jpg"), **{kwargs_repr})
                print("RESULT_IS_NONE", r is None)
            """
        # Act
        out = _run_capture_subprocess(tmp_path, body)
        # Assert
        assert "RESULT_IS_NONE True" in out


class TestCaptureURLCapture:
    """URL capture returns None when playwright is unavailable + not WSL."""

    def test_url_capture_returns_none_without_playwright(self, tmp_path):
        # Arrange
        body = """
            from scitex_capture.utils import capture
            with tempfile.TemporaryDirectory() as d:
                r = capture(
                    url="http://localhost:8000",
                    path=os.path.join(d, "t.jpg"),
                    verbose=False,
                )
                print("RESULT_IS_NONE", r is None)
            """
        # Act
        out = _run_capture_subprocess(tmp_path, body, blocked_modules=("playwright",))
        # Assert
        assert "RESULT_IS_NONE True" in out


class TestCaptureAppCapture:
    """App-specific capture returns None when no window matches."""

    def test_unknown_app_returns_none(self):
        # Arrange
        from scitex_capture.utils import capture

        # A process name that will not be running on any host.
        absent_app = "scitex_capture_definitely_absent_app_xyz"
        # Act
        result = capture(app=absent_app, verbose=False)
        # Assert
        assert result is None


class TestTakeScreenshot:
    """take_screenshot() returns None when capture fails."""

    @pytest.mark.parametrize(
        "kwargs_repr",
        [
            "dict()",
            'dict(output_path=os.path.join(d, "custom.jpg"))',
            "dict(jpeg=True, quality=50)",
        ],
        ids=["defaults", "custom_path", "quality"],
    )
    def test_take_screenshot_returns_none_for_each_param_set(
        self, tmp_path, kwargs_repr
    ):
        # Arrange
        body = f"""
            from scitex_capture.utils import take_screenshot
            with tempfile.TemporaryDirectory() as d:
                r = take_screenshot(**{kwargs_repr})
                print("RESULT_IS_NONE", r is None)
            """
        # Act
        out = _run_capture_subprocess(tmp_path, body)
        # Assert
        assert "RESULT_IS_NONE True" in out


class TestStartStopMonitor:
    """start_monitor / stop_monitor run the real worker lifecycle."""

    def test_start_monitor_returns_a_screenshot_worker(self, tmp_path):
        # Arrange
        from scitex_capture.capture import ScreenshotWorker
        from scitex_capture.utils import start_monitor, stop_monitor

        # Act
        worker = start_monitor(output_dir=str(tmp_path), interval=0.5, verbose=False)
        try:
            # Assert
            assert isinstance(worker, ScreenshotWorker)
        finally:
            stop_monitor()

    def test_start_monitor_marks_worker_running(self, tmp_path):
        # Arrange
        from scitex_capture.utils import start_monitor, stop_monitor

        # Act
        worker = start_monitor(output_dir=str(tmp_path), interval=0.5, verbose=False)
        try:
            # Assert
            assert worker.running is True
        finally:
            stop_monitor()

    def test_stop_monitor_stops_the_worker(self, tmp_path):
        # Arrange
        from scitex_capture.utils import start_monitor, stop_monitor

        worker = start_monitor(output_dir=str(tmp_path), interval=0.5, verbose=False)
        # Act
        stop_monitor()
        # Assert
        assert worker.running is False

    def test_start_monitor_forwards_on_capture_callback(self, tmp_path):
        # Arrange
        from scitex_capture.utils import start_monitor, stop_monitor

        callback = lambda p: None
        # Act
        worker = start_monitor(
            output_dir=str(tmp_path), on_capture=callback, verbose=False
        )
        try:
            # Assert
            assert worker.on_capture is callback
        finally:
            stop_monitor()

    def test_start_monitor_forwards_on_error_callback(self, tmp_path):
        # Arrange
        from scitex_capture.utils import start_monitor, stop_monitor

        callback = lambda e: None
        # Act
        worker = start_monitor(
            output_dir=str(tmp_path), on_error=callback, verbose=False
        )
        try:
            # Assert
            assert worker.on_error is callback
        finally:
            stop_monitor()

    def test_start_monitor_forwards_monitor_id(self, tmp_path):
        # Arrange
        from scitex_capture.utils import start_monitor, stop_monitor

        # Act
        worker = start_monitor(
            output_dir=str(tmp_path), monitor_id=2, capture_all=True, verbose=False
        )
        try:
            # Assert
            assert worker.monitor == 2
        finally:
            stop_monitor()

    def test_start_monitor_forwards_capture_all(self, tmp_path):
        # Arrange
        from scitex_capture.utils import start_monitor, stop_monitor

        # Act
        worker = start_monitor(
            output_dir=str(tmp_path), monitor_id=2, capture_all=True, verbose=False
        )
        try:
            # Assert
            assert worker.capture_all is True
        finally:
            stop_monitor()

    def test_stop_monitor_when_not_started_returns_none(self):
        # Arrange
        from scitex_capture.utils import stop_monitor

        # Act
        result = stop_monitor()
        # Assert
        assert result is None


class TestCacheSizeManagement:
    """Test cache size management against real files."""

    def test_files_under_limit_are_kept(self, tmp_path):
        # Arrange
        from scitex_capture.utils import _manage_cache_size

        for i in range(5):
            (tmp_path / f"test_{i}.jpg").write_bytes(b"x" * 100)
        # Act
        _manage_cache_size(tmp_path, max_size_gb=1.0)
        # Assert
        assert len(list(tmp_path.glob("*.jpg"))) == 5

    def test_oldest_files_are_deleted_when_over_limit(self, tmp_path):
        # Arrange
        from scitex_capture.utils import _manage_cache_size

        for i in range(5):
            (tmp_path / f"test_{i}.jpg").write_bytes(b"x" * 1_024 * 1_024)
            time.sleep(0.05)  # ensure distinct mtimes
        # Act
        _manage_cache_size(tmp_path, max_size_gb=0.000002)
        # Assert
        assert len(list(tmp_path.glob("*.jpg"))) < 5

    def test_nonexistent_dir_returns_none(self):
        # Arrange
        from scitex_capture.utils import _manage_cache_size

        # Act
        result = _manage_cache_size(Path("/nonexistent/path"), max_size_gb=1.0)
        # Assert
        assert result is None

    def test_png_files_under_limit_are_kept(self, tmp_path):
        # Arrange
        from scitex_capture.utils import _manage_cache_size

        for i in range(3):
            (tmp_path / f"test_{i}.png").write_bytes(b"x" * 100)
        # Act
        _manage_cache_size(tmp_path, max_size_gb=1.0)
        # Assert
        assert len(list(tmp_path.glob("*.png"))) == 3


class TestCategoryDetection:
    """Test _detect_category against real images and filenames."""

    def test_plain_white_image_is_stdout(self, tmp_path):
        # Arrange
        Image = pytest.importorskip("PIL.Image")
        from scitex_capture.utils import _detect_category

        test_file = tmp_path / "test.jpg"
        Image.new("RGB", (10, 10), color="white").save(test_file)
        # Act
        result = _detect_category(str(test_file))
        # Assert
        assert result == "stdout"

    def test_red_dominant_image_is_error(self, tmp_path):
        # Arrange
        Image = pytest.importorskip("PIL.Image")
        from scitex_capture.utils import _detect_category

        test_file = tmp_path / "test.jpg"
        Image.new("RGB", (100, 100), color=(255, 50, 50)).save(test_file)
        # Act
        result = _detect_category(str(test_file))
        # Assert
        assert result == "error"

    def test_error_keyword_in_filename_is_stderr(self):
        # Arrange
        from scitex_capture.utils import _detect_category

        # Act
        result = _detect_category("/path/to/error_screenshot.jpg")
        # Assert
        assert result == "stderr"

    def test_fail_keyword_in_filename_is_stderr(self):
        # Arrange
        from scitex_capture.utils import _detect_category

        # Act
        result = _detect_category("/path/to/fail_test.jpg")
        # Assert
        assert result == "stderr"

    def test_warning_keyword_in_filename_is_stderr(self):
        # Arrange
        from scitex_capture.utils import _detect_category

        # Act
        result = _detect_category("/path/to/warning_dialog.jpg")
        # Assert
        assert result == "stderr"

    def test_missing_file_defaults_to_stdout(self):
        # Arrange
        from scitex_capture.utils import _detect_category

        # Act
        result = _detect_category("/nonexistent/file.jpg")
        # Assert
        assert result == "stdout"


class TestExceptionContextDetection:
    """Test _is_in_exception_context."""

    def test_returns_false_outside_an_except_block(self):
        # Arrange
        from scitex_capture.utils import _is_in_exception_context

        # Act
        result = _is_in_exception_context()
        # Assert
        assert result is False

    def test_returns_true_inside_an_except_block(self):
        # Arrange
        from scitex_capture.utils import _is_in_exception_context

        # Act
        try:
            raise ValueError("Test error")
        except ValueError:
            result = _is_in_exception_context()
        # Assert
        assert result is True


class TestMessageMetadata:
    """Test _add_message_metadata with real PIL and a real PIL-absent fallback."""

    def test_with_pil_leaves_the_image_in_place(self, tmp_path):
        # Arrange
        Image = pytest.importorskip("PIL.Image")
        from scitex_capture.utils import _add_message_metadata

        test_file = tmp_path / "test.jpg"
        Image.new("RGB", (10, 10), color="white").save(test_file)
        # Act
        _add_message_metadata(str(test_file), "Test message")
        # Assert
        assert test_file.exists()

    def test_without_pil_creates_companion_text_file(self, tmp_path):
        # Arrange
        stub_root = tmp_path / "stubs"
        (stub_root / "PIL").mkdir(parents=True)
        (stub_root / "PIL" / "__init__.py").write_text(
            'raise ImportError("PIL blocked for test")\n'
        )
        target = tmp_path / "test.jpg"
        target.touch()
        script = tmp_path / "child.py"
        script.write_text(
            textwrap.dedent(
                f"""
                from scitex_capture.utils import _add_message_metadata
                _add_message_metadata({str(target)!r}, "Test message")
                from pathlib import Path
                txt = Path({str(target)!r}).with_suffix(".txt")
                print("TXT_EXISTS", txt.exists())
                print("TXT_HAS_MSG", "Test message" in txt.read_text())
                """
            )
        )
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join([str(stub_root), env.get("PYTHONPATH", "")])
        # Act
        proc = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )
        # Assert
        assert "TXT_EXISTS True" in proc.stdout

    def test_without_pil_text_file_contains_the_message(self, tmp_path):
        # Arrange
        stub_root = tmp_path / "stubs"
        (stub_root / "PIL").mkdir(parents=True)
        (stub_root / "PIL" / "__init__.py").write_text(
            'raise ImportError("PIL blocked for test")\n'
        )
        target = tmp_path / "test.jpg"
        target.touch()
        script = tmp_path / "child.py"
        script.write_text(
            textwrap.dedent(
                f"""
                from scitex_capture.utils import _add_message_metadata
                _add_message_metadata({str(target)!r}, "Test message")
                from pathlib import Path
                txt = Path({str(target)!r}).with_suffix(".txt")
                print("TXT_HAS_MSG", "Test message" in txt.read_text())
                """
            )
        )
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join([str(stub_root), env.get("PYTHONPATH", "")])
        # Act
        proc = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )
        # Assert
        assert "TXT_HAS_MSG True" in proc.stdout


class TestModuleExports:
    """Test module exports."""

    def test_every_all_export_is_an_attribute(self):
        # Arrange
        from scitex_capture import utils

        # Act
        present = {n for n in utils.__all__ if hasattr(utils, n)}
        # Assert
        assert present == set(utils.__all__)

    def test_capture_is_callable(self):
        # Arrange
        # Act
        from scitex_capture.utils import capture

        # Assert
        assert callable(capture)

    def test_take_screenshot_is_callable(self):
        # Arrange
        # Act
        from scitex_capture.utils import take_screenshot

        # Assert
        assert callable(take_screenshot)

    def test_start_monitor_is_callable(self):
        # Arrange
        # Act
        from scitex_capture.utils import start_monitor

        # Assert
        assert callable(start_monitor)

    def test_stop_monitor_is_callable(self):
        # Arrange
        # Act
        from scitex_capture.utils import stop_monitor

        # Assert
        assert callable(stop_monitor)


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
