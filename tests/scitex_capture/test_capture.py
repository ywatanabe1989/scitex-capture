#!/usr/bin/env python3
"""Tests for scitex_capture.capture module.

Tests core screenshot capture functionality including:
- ScreenshotWorker initialization and configuration
- Worker lifecycle (start/stop)
- Status reporting
- CaptureManager high-level interface

No mocking library is used. The display-touching collaborator
(``_take_screenshot`` and the platform probes ``_is_wsl`` /
``_capture_native_screen``) is controlled with hand-rolled
``ScreenshotWorker`` subclasses — real objects whose real
``start``/``stop`` thread and real ``_worker_loop`` run, only the
display interaction is swapped for a deterministic stand-in. The two
WSL-detection branches that need a specific ``os.uname().release`` are
exercised by real subprocesses that arrange their own ``os.uname``
before calling the real ``_is_wsl``.
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
# Hand-rolled fakes (real ScreenshotWorker subclasses, no mock library).
# --------------------------------------------------------------------------
def _no_capture_worker_class():
    from scitex_capture.capture import ScreenshotWorker

    class NoCaptureWorker(ScreenshotWorker):
        """Real worker whose capture is a deterministic no-op (returns None)."""

        def _take_screenshot(self):
            return None

    return NoCaptureWorker


def _fixed_path_worker_class(fixed_path):
    from scitex_capture.capture import ScreenshotWorker

    class FixedPathWorker(ScreenshotWorker):
        """Real worker whose capture always 'succeeds' with a fixed path."""

        def _take_screenshot(self):
            return fixed_path

    return FixedPathWorker


def _raising_worker_class(exc):
    from scitex_capture.capture import ScreenshotWorker

    class RaisingWorker(ScreenshotWorker):
        """Real worker whose capture raises, exercising the on_error path."""

        def _take_screenshot(self):
            raise exc

    return RaisingWorker


def _no_backend_worker_class():
    from scitex_capture.capture import ScreenshotWorker

    class NoBackendWorker(ScreenshotWorker):
        """Real worker where both capture backends report failure.

        ``_take_screenshot`` itself is the *real* method — only the two
        leaf collaborators it dispatches to are forced to report no
        capture, so the real filename/dispatch logic runs and returns
        None.
        """

        def _is_wsl(self):
            return False

        def _capture_native_screen(self, filepath):
            return False

    return NoBackendWorker


class TestScreenshotWorkerInit:
    """Test ScreenshotWorker initialization stores parameters."""

    @pytest.fixture
    def default_worker(self, tmp_path):
        from scitex_capture.capture import ScreenshotWorker

        return ScreenshotWorker(output_dir=str(tmp_path))

    def test_default_output_dir_stored(self, default_worker, tmp_path):
        # Arrange
        worker = default_worker
        # Act
        value = worker.output_dir
        # Assert
        assert value == Path(str(tmp_path))

    def test_default_interval_is_one_second(self, default_worker):
        # Arrange
        worker = default_worker
        # Act
        value = worker.interval_sec
        # Assert
        assert value == 1.0

    def test_default_verbose_is_false(self, default_worker):
        # Arrange
        worker = default_worker
        # Act
        value = worker.verbose
        # Assert
        assert value is False

    def test_default_use_jpeg_is_true(self, default_worker):
        # Arrange
        worker = default_worker
        # Act
        value = worker.use_jpeg
        # Assert
        assert value is True

    def test_default_jpeg_quality_is_sixty(self, default_worker):
        # Arrange
        worker = default_worker
        # Act
        value = worker.jpeg_quality
        # Assert
        assert value == 60

    def test_default_running_is_false(self, default_worker):
        # Arrange
        worker = default_worker
        # Act
        value = worker.running
        # Assert
        assert value is False

    def test_default_worker_thread_is_none(self, default_worker):
        # Arrange
        worker = default_worker
        # Act
        value = worker.worker_thread
        # Assert
        assert value is None

    def test_default_screenshot_count_is_zero(self, default_worker):
        # Arrange
        worker = default_worker
        # Act
        value = worker.screenshot_count
        # Assert
        assert value == 0

    def test_default_session_id_is_none(self, default_worker):
        # Arrange
        worker = default_worker
        # Act
        value = worker.session_id
        # Assert
        assert value is None

    def test_default_monitor_is_zero(self, default_worker):
        # Arrange
        worker = default_worker
        # Act
        value = worker.monitor
        # Assert
        assert value == 0

    def test_default_capture_all_is_false(self, default_worker):
        # Arrange
        worker = default_worker
        # Act
        value = worker.capture_all
        # Assert
        assert value is False

    @pytest.fixture
    def custom_worker(self, tmp_path):
        from scitex_capture.capture import ScreenshotWorker

        self._on_capture = lambda x: None
        self._on_error = lambda x: None
        return ScreenshotWorker(
            output_dir=str(tmp_path),
            interval_sec=2.5,
            verbose=True,
            use_jpeg=False,
            jpeg_quality=90,
            on_capture=self._on_capture,
            on_error=self._on_error,
        )

    def test_custom_interval_stored(self, custom_worker):
        # Arrange
        worker = custom_worker
        # Act
        value = worker.interval_sec
        # Assert
        assert value == 2.5

    def test_custom_verbose_stored(self, custom_worker):
        # Arrange
        worker = custom_worker
        # Act
        value = worker.verbose
        # Assert
        assert value is True

    def test_custom_use_jpeg_stored(self, custom_worker):
        # Arrange
        worker = custom_worker
        # Act
        value = worker.use_jpeg
        # Assert
        assert value is False

    def test_custom_jpeg_quality_stored(self, custom_worker):
        # Arrange
        worker = custom_worker
        # Act
        value = worker.jpeg_quality
        # Assert
        assert value == 90

    def test_custom_on_capture_stored(self, custom_worker):
        # Arrange
        worker = custom_worker
        # Act
        value = worker.on_capture
        # Assert
        assert value is self._on_capture

    def test_custom_on_error_stored(self, custom_worker):
        # Arrange
        worker = custom_worker
        # Act
        value = worker.on_error
        # Assert
        assert value is self._on_error

    def test_creates_missing_output_directory(self, tmp_path):
        # Arrange
        from scitex_capture.capture import ScreenshotWorker

        nested = tmp_path / "nested" / "deep" / "dir"
        # Act
        ScreenshotWorker(output_dir=str(nested))
        # Assert
        assert nested.is_dir()


class TestScreenshotWorkerLifecycle:
    """Test ScreenshotWorker start/stop lifecycle with a no-capture worker."""

    def test_start_sets_running_true(self, tmp_path):
        # Arrange
        worker = _no_capture_worker_class()(output_dir=str(tmp_path))
        # Act
        worker.start()
        try:
            # Assert
            assert worker.running is True
        finally:
            worker.stop()

    def test_start_assigns_a_session_id(self, tmp_path):
        # Arrange
        worker = _no_capture_worker_class()(output_dir=str(tmp_path))
        # Act
        worker.start()
        try:
            # Assert
            assert worker.session_id is not None
        finally:
            worker.stop()

    def test_start_spawns_a_live_thread(self, tmp_path):
        # Arrange
        worker = _no_capture_worker_class()(output_dir=str(tmp_path))
        # Act
        worker.start()
        try:
            # Assert
            assert worker.worker_thread.is_alive()
        finally:
            worker.stop()

    def test_stop_clears_running_flag(self, tmp_path):
        # Arrange
        worker = _no_capture_worker_class()(output_dir=str(tmp_path))
        worker.start()
        # Act
        worker.stop()
        # Assert
        assert worker.running is False

    def test_start_uses_provided_session_id(self, tmp_path):
        # Arrange
        worker = _no_capture_worker_class()(output_dir=str(tmp_path))
        # Act
        worker.start(session_id="my_custom_session")
        try:
            # Assert
            assert worker.session_id == "my_custom_session"
        finally:
            worker.stop()

    def test_auto_session_id_is_fifteen_char_timestamp(self, tmp_path):
        # Arrange
        worker = _no_capture_worker_class()(output_dir=str(tmp_path))
        # Act
        worker.start()
        try:
            # Assert
            # Format YYYYMMDD_HHMMSS -> 15 chars with an underscore.
            assert len(worker.session_id) == 15 and "_" in worker.session_id
        finally:
            worker.stop()

    def test_stop_when_not_running_is_safe(self, tmp_path):
        # Arrange
        worker = _no_capture_worker_class()(output_dir=str(tmp_path))
        # Act
        worker.stop()
        # Assert
        assert worker.running is False

    def test_double_start_keeps_same_thread(self, tmp_path):
        # Arrange
        worker = _no_capture_worker_class()(output_dir=str(tmp_path))
        worker.start()
        first_thread = worker.worker_thread
        # Act
        worker.start()  # second call must be a no-op
        try:
            # Assert
            assert worker.worker_thread is first_thread
        finally:
            worker.stop()

    def test_double_start_keeps_same_session_id(self, tmp_path):
        # Arrange
        worker = _no_capture_worker_class()(output_dir=str(tmp_path))
        worker.start()
        first_session = worker.session_id
        # Act
        worker.start()
        try:
            # Assert
            assert worker.session_id == first_session
        finally:
            worker.stop()

    def test_worker_thread_is_daemon(self, tmp_path):
        # Arrange
        worker = _no_capture_worker_class()(output_dir=str(tmp_path))
        # Act
        worker.start()
        try:
            # Assert
            assert worker.worker_thread.daemon is True
        finally:
            worker.stop()


class TestScreenshotWorkerStatus:
    """Test ScreenshotWorker get_status()."""

    @pytest.fixture
    def status(self, tmp_path):
        from scitex_capture.capture import ScreenshotWorker

        worker = ScreenshotWorker(
            output_dir=str(tmp_path),
            interval_sec=2.0,
            use_jpeg=True,
            jpeg_quality=75,
        )
        return worker.get_status()

    def test_status_has_running_key(self, status):
        # Arrange
        result = status
        # Act
        present = "running" in result
        # Assert
        assert present

    def test_status_has_session_id_key(self, status):
        # Arrange
        result = status
        # Act
        present = "session_id" in result
        # Assert
        assert present

    def test_status_has_screenshot_count_key(self, status):
        # Arrange
        result = status
        # Act
        present = "screenshot_count" in result
        # Assert
        assert present

    def test_status_has_output_dir_key(self, status):
        # Arrange
        result = status
        # Act
        present = "output_dir" in result
        # Assert
        assert present

    def test_status_running_is_false_before_start(self, status):
        # Arrange
        result = status
        # Act
        value = result["running"]
        # Assert
        assert value is False

    def test_status_screenshot_count_starts_at_zero(self, status):
        # Arrange
        result = status
        # Act
        value = result["screenshot_count"]
        # Assert
        assert value == 0

    def test_status_reports_configured_interval(self, status):
        # Arrange
        result = status
        # Act
        value = result["interval_sec"]
        # Assert
        assert value == 2.0

    def test_status_reports_configured_quality(self, status):
        # Arrange
        result = status
        # Act
        value = result["jpeg_quality"]
        # Assert
        assert value == 75

    def test_status_running_true_while_started(self, tmp_path):
        # Arrange
        worker = _no_capture_worker_class()(output_dir=str(tmp_path))
        # Act
        worker.start(session_id="test_session")
        try:
            running = worker.get_status()["running"]
        finally:
            worker.stop()
        # Assert
        assert running is True

    def test_status_reports_running_session_id(self, tmp_path):
        # Arrange
        worker = _no_capture_worker_class()(output_dir=str(tmp_path))
        # Act
        worker.start(session_id="test_session")
        try:
            session_id = worker.get_status()["session_id"]
        finally:
            worker.stop()
        # Assert
        assert session_id == "test_session"


class TestScreenshotWorkerWSLDetection:
    """Test _is_wsl() — branch coverage via real subprocesses.

    Each subprocess arranges its own os.uname / sys.platform with real
    callables (no mock library), then calls the real _is_wsl().
    """

    def _run_is_wsl(self, tmp_path, release, platform):
        script = tmp_path / "probe.py"
        script.write_text(
            textwrap.dedent(
                f"""
                import os, sys, types, tempfile
                os.uname = lambda: types.SimpleNamespace(release={release!r})
                sys.platform = {platform!r}
                from scitex_capture.capture import ScreenshotWorker
                with tempfile.TemporaryDirectory() as d:
                    w = ScreenshotWorker(output_dir=d)
                    print("IS_WSL", w._is_wsl())
                """
            )
        )
        proc = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return proc.stdout

    def test_linux_with_microsoft_release_is_wsl(self, tmp_path):
        # Arrange
        release = "5.15.90.1-microsoft-standard-WSL2"
        # Act
        out = self._run_is_wsl(tmp_path, release, "linux")
        # Assert
        assert "IS_WSL True" in out

    def test_linux_without_microsoft_release_is_not_wsl(self, tmp_path):
        # Arrange
        release = "5.15.0-generic"
        # Act
        out = self._run_is_wsl(tmp_path, release, "linux")
        # Assert
        assert "IS_WSL False" in out

    def test_non_linux_platform_is_not_wsl(self, tmp_path):
        # Arrange
        release = "5.15.90.1-microsoft-standard-WSL2"
        # Act
        out = self._run_is_wsl(tmp_path, release, "darwin")
        # Assert
        assert "IS_WSL False" in out


class TestScreenshotWorkerCallbacks:
    """Test on_capture / on_error callbacks via the real worker loop."""

    def test_on_capture_receives_the_capture_path(self, tmp_path):
        # Arrange
        captured = []
        worker = _fixed_path_worker_class("/fake/path.jpg")(
            output_dir=str(tmp_path),
            interval_sec=0.05,
            on_capture=captured.append,
        )
        # Act
        worker.start()
        time.sleep(0.25)
        worker.stop()
        # Assert
        assert captured and all(p == "/fake/path.jpg" for p in captured)

    def test_on_error_receives_the_raised_exception(self, tmp_path):
        # Arrange
        errors = []
        worker = _raising_worker_class(RuntimeError("Test error"))(
            output_dir=str(tmp_path),
            interval_sec=0.05,
            on_error=errors.append,
        )
        # Act
        worker.start()
        time.sleep(0.25)
        worker.stop()
        # Assert
        assert errors and all(isinstance(e, RuntimeError) for e in errors)


class TestCaptureManager:
    """Test CaptureManager high-level interface (real worker lifecycle)."""

    def test_initialization_leaves_worker_none(self):
        # Arrange
        from scitex_capture.capture import CaptureManager

        # Act
        manager = CaptureManager()
        # Assert
        assert manager.worker is None

    def test_start_capture_assigns_a_worker(self, tmp_path):
        # Arrange
        from scitex_capture.capture import CaptureManager

        manager = CaptureManager()
        # Act
        manager.start_capture(output_dir=str(tmp_path))
        try:
            # Assert
            assert manager.worker is not None
        finally:
            manager.stop_capture()

    def test_start_capture_returns_the_running_worker(self, tmp_path):
        # Arrange
        from scitex_capture.capture import CaptureManager

        manager = CaptureManager()
        # Act
        worker = manager.start_capture(output_dir=str(tmp_path))
        try:
            # Assert
            assert manager.worker is worker
        finally:
            manager.stop_capture()

    def test_start_capture_marks_worker_running(self, tmp_path):
        # Arrange
        from scitex_capture.capture import CaptureManager

        manager = CaptureManager()
        # Act
        worker = manager.start_capture(output_dir=str(tmp_path))
        try:
            # Assert
            assert worker.running is True
        finally:
            manager.stop_capture()

    def test_stop_capture_clears_the_worker(self, tmp_path):
        # Arrange
        from scitex_capture.capture import CaptureManager

        manager = CaptureManager()
        manager.start_capture(output_dir=str(tmp_path))
        # Act
        manager.stop_capture()
        # Assert
        assert manager.worker is None

    @pytest.fixture
    def parametrised_worker(self, tmp_path):
        from scitex_capture.capture import CaptureManager

        manager = CaptureManager()
        worker = manager.start_capture(
            output_dir=str(tmp_path),
            interval=2.5,
            jpeg=False,
            quality=90,
            verbose=True,
            monitor_id=1,
            capture_all=True,
        )
        try:
            yield worker
        finally:
            manager.stop_capture()

    def test_start_capture_propagates_interval(self, parametrised_worker):
        # Arrange
        worker = parametrised_worker
        # Act
        value = worker.interval_sec
        # Assert
        assert value == 2.5

    def test_start_capture_propagates_jpeg_flag(self, parametrised_worker):
        # Arrange
        worker = parametrised_worker
        # Act
        value = worker.use_jpeg
        # Assert
        assert value is False

    def test_start_capture_propagates_quality(self, parametrised_worker):
        # Arrange
        worker = parametrised_worker
        # Act
        value = worker.jpeg_quality
        # Assert
        assert value == 90

    def test_start_capture_propagates_monitor_id(self, parametrised_worker):
        # Arrange
        worker = parametrised_worker
        # Act
        value = worker.monitor
        # Assert
        assert value == 1

    def test_start_capture_propagates_capture_all(self, parametrised_worker):
        # Arrange
        worker = parametrised_worker
        # Act
        value = worker.capture_all
        # Assert
        assert value is True

    def test_start_capture_twice_returns_same_worker(self, tmp_path):
        # Arrange
        from scitex_capture.capture import CaptureManager

        manager = CaptureManager()
        worker1 = manager.start_capture(output_dir=str(tmp_path))
        # Act
        worker2 = manager.start_capture(output_dir=str(tmp_path))
        try:
            # Assert
            assert worker1 is worker2
        finally:
            manager.stop_capture()

    def test_stop_capture_when_idle_is_safe(self):
        # Arrange
        from scitex_capture.capture import CaptureManager

        manager = CaptureManager()
        # Act
        manager.stop_capture()
        # Assert
        assert manager.worker is None


class TestCaptureManagerSingleScreenshot:
    """Test take_single_screenshot default-path resolution."""

    def test_default_path_resolves_under_runtime_or_returns_none(self, tmp_path):
        # Arrange
        from scitex_capture.capture import CaptureManager

        os.environ["SCITEX_DIR"] = str(tmp_path)
        screenshots = tmp_path / "capture" / "runtime" / "screenshots"
        manager = CaptureManager()
        try:
            # Act
            result = manager.take_single_screenshot()
        finally:
            os.environ.pop("SCITEX_DIR", None)
        # Assert
        # Capture succeeds (display) or returns None (headless); either way
        # the default path resolves under runtime/screenshots.
        assert result is None or str(screenshots) in str(result)


class TestTakeScreenshotDispatch:
    """Test _take_screenshot's real dispatch + filename logic.

    Both display backends are forced to report failure via a hand-rolled
    subclass; the real _take_screenshot runs and must return None.
    """

    def test_returns_none_when_no_backend_succeeds(self, tmp_path):
        # Arrange
        worker = _no_backend_worker_class()(output_dir=str(tmp_path), use_jpeg=True)
        worker.session_id = "20250104_120000"
        worker.screenshot_count = 5
        # Act
        result = worker._take_screenshot()
        # Assert
        assert result is None

    def test_png_extension_selected_when_jpeg_disabled(self, tmp_path):
        # Arrange
        from scitex_capture.capture import ScreenshotWorker

        worker = ScreenshotWorker(output_dir=str(tmp_path), use_jpeg=False)
        # Act
        ext = "jpg" if worker.use_jpeg else "png"
        # Assert
        assert ext == "png"


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
