#!/usr/bin/env python3
"""Tests for scitex_capture.session module.

Tests Session context manager for automatic capture start/stop:
- Session initialization with parameters
- Context manager protocol (__enter__/__exit__)
- session() factory function

The context-manager tests run the *real* Session lifecycle: __enter__
spawns a real ScreenshotWorker daemon thread and __exit__ joins it.
The worker's screenshot attempts land in a TemporaryDirectory (or
fail harmlessly when headless); the lifecycle assertions (running
flags, parameter propagation, __exit__ return) are independent of
whether any screenshot actually succeeds, so no collaborator needs to
be faked.
"""

import os
import tempfile

import pytest


class TestSessionInit:
    """Test Session default-parameter initialization."""

    def test_default_output_dir_is_none(self):
        # Arrange
        from scitex_capture.session import Session

        # Act
        sess = Session()
        # Assert
        # None means start_monitor lazily resolves the canonical
        # $SCITEX_DIR/capture/runtime/screenshots/ path at use time.
        assert sess.output_dir is None

    def test_default_interval_is_one_second(self):
        # Arrange
        from scitex_capture.session import Session

        # Act
        sess = Session()
        # Assert
        assert sess.interval == 1.0

    def test_default_jpeg_is_true(self):
        # Arrange
        from scitex_capture.session import Session

        # Act
        sess = Session()
        # Assert
        assert sess.jpeg is True

    def test_default_quality_is_sixty(self):
        # Arrange
        from scitex_capture.session import Session

        # Act
        sess = Session()
        # Assert
        assert sess.quality == 60

    def test_default_on_capture_is_none(self):
        # Arrange
        from scitex_capture.session import Session

        # Act
        sess = Session()
        # Assert
        assert sess.on_capture is None

    def test_default_on_error_is_none(self):
        # Arrange
        from scitex_capture.session import Session

        # Act
        sess = Session()
        # Assert
        assert sess.on_error is None

    def test_default_verbose_is_true(self):
        # Arrange
        from scitex_capture.session import Session

        # Act
        sess = Session()
        # Assert
        assert sess.verbose is True

    def test_default_monitor_id_is_zero(self):
        # Arrange
        from scitex_capture.session import Session

        # Act
        sess = Session()
        # Assert
        assert sess.monitor_id == 0

    def test_default_capture_all_is_false(self):
        # Arrange
        from scitex_capture.session import Session

        # Act
        sess = Session()
        # Assert
        assert sess.capture_all is False

    def test_default_worker_is_none(self):
        # Arrange
        from scitex_capture.session import Session

        # Act
        sess = Session()
        # Assert
        assert sess.worker is None


@pytest.fixture
def callbacks():
    """A pair of distinct no-op callbacks for identity assertions."""
    return (lambda x: None, lambda x: None)


@pytest.fixture
def custom_session(callbacks):
    """A Session built with every parameter set to a non-default value.

    Built via the ``session()`` factory (not ``Session(...)`` directly):
    the object is a context manager that acquires nothing until
    ``__enter__`` — it is never entered here, so there is no resource to
    clean up.
    """
    from scitex_capture.session import session as make_session

    on_capture, on_error = callbacks
    return make_session(
        output_dir="/custom/path",
        interval=2.5,
        jpeg=False,
        quality=90,
        on_capture=on_capture,
        on_error=on_error,
        verbose=False,
        monitor_id=1,
        capture_all=True,
    )


class TestSessionCustomInit:
    """Test Session stores every custom-init parameter verbatim."""

    def test_custom_output_dir_stored(self, custom_session):
        # Arrange
        sess = custom_session
        # Act
        value = sess.output_dir
        # Assert
        assert value == "/custom/path"

    def test_custom_interval_stored(self, custom_session):
        # Arrange
        sess = custom_session
        # Act
        value = sess.interval
        # Assert
        assert value == 2.5

    def test_custom_jpeg_stored(self, custom_session):
        # Arrange
        sess = custom_session
        # Act
        value = sess.jpeg
        # Assert
        assert value is False

    def test_custom_quality_stored(self, custom_session):
        # Arrange
        sess = custom_session
        # Act
        value = sess.quality
        # Assert
        assert value == 90

    def test_custom_on_capture_stored(self, custom_session, callbacks):
        # Arrange
        sess = custom_session
        expected, _ = callbacks
        # Act
        value = sess.on_capture
        # Assert
        assert value is expected

    def test_custom_on_error_stored(self, custom_session, callbacks):
        # Arrange
        sess = custom_session
        _, expected = callbacks
        # Act
        value = sess.on_error
        # Assert
        assert value is expected

    def test_custom_verbose_stored(self, custom_session):
        # Arrange
        sess = custom_session
        # Act
        value = sess.verbose
        # Assert
        assert value is False

    def test_custom_monitor_id_stored(self, custom_session):
        # Arrange
        sess = custom_session
        # Act
        value = sess.monitor_id
        # Assert
        assert value == 1

    def test_custom_capture_all_stored(self, custom_session):
        # Arrange
        sess = custom_session
        # Act
        value = sess.capture_all
        # Assert
        assert value is True


class TestSessionContextManager:
    """Test the real Session context manager protocol."""

    def test_enter_returns_the_session_object(self):
        # Arrange
        from scitex_capture.session import Session

        with tempfile.TemporaryDirectory() as tmpdir:
            sess = Session(output_dir=tmpdir, verbose=False)
            # Act
            result = sess.__enter__()
            try:
                # Assert
                assert result is sess
            finally:
                sess.__exit__(None, None, None)

    def test_enter_creates_a_worker(self):
        # Arrange
        from scitex_capture.session import Session

        with tempfile.TemporaryDirectory() as tmpdir:
            sess = Session(output_dir=tmpdir, verbose=False)
            # Act
            sess.__enter__()
            try:
                # Assert
                assert sess.worker is not None
            finally:
                sess.__exit__(None, None, None)

    def test_enter_marks_worker_running(self):
        # Arrange
        from scitex_capture.session import Session

        with tempfile.TemporaryDirectory() as tmpdir:
            sess = Session(output_dir=tmpdir, verbose=False)
            # Act
            sess.__enter__()
            try:
                # Assert
                assert sess.worker.running is True
            finally:
                sess.__exit__(None, None, None)

    def test_exit_stops_the_worker(self):
        # Arrange
        from scitex_capture.session import Session

        with tempfile.TemporaryDirectory() as tmpdir:
            sess = Session(output_dir=tmpdir, verbose=False)
            sess.__enter__()
            worker = sess.worker
            # Act
            sess.__exit__(None, None, None)
            # Assert
            assert worker.running is False

    def test_exit_returns_false_to_not_suppress_exceptions(self):
        # Arrange
        from scitex_capture.session import Session

        with tempfile.TemporaryDirectory() as tmpdir:
            sess = Session(output_dir=tmpdir, verbose=False)
            sess.__enter__()
            # Act
            result = sess.__exit__(ValueError, ValueError("test"), None)
            # Assert
            assert result is False

    def test_with_statement_starts_worker_inside_block(self):
        # Arrange
        from scitex_capture.session import Session

        with tempfile.TemporaryDirectory() as tmpdir:
            # Act
            with Session(output_dir=tmpdir, verbose=False) as sess:
                running_inside = sess.worker.running
            # Assert
            assert running_inside is True

    def test_with_statement_stops_worker_after_block(self):
        # Arrange
        from scitex_capture.session import Session

        with tempfile.TemporaryDirectory() as tmpdir:
            # Act
            with Session(output_dir=tmpdir, verbose=False) as sess:
                worker = sess.worker
            # Assert
            assert worker.running is False


class TestSessionParameterPropagation:
    """Each Session parameter must reach the underlying worker."""

    @pytest.fixture
    def running_worker(self):
        from scitex_capture.session import Session

        with tempfile.TemporaryDirectory() as tmpdir:
            with Session(
                output_dir=tmpdir,
                interval=0.5,
                jpeg=False,
                quality=80,
                verbose=False,
                monitor_id=2,
                capture_all=True,
            ) as sess:
                yield sess.worker

    def test_interval_propagates_to_worker(self, running_worker):
        # Arrange
        worker = running_worker
        # Act
        value = worker.interval_sec
        # Assert
        assert value == 0.5

    def test_jpeg_flag_propagates_to_worker(self, running_worker):
        # Arrange
        worker = running_worker
        # Act
        value = worker.use_jpeg
        # Assert
        assert value is False

    def test_quality_propagates_to_worker(self, running_worker):
        # Arrange
        worker = running_worker
        # Act
        value = worker.jpeg_quality
        # Assert
        assert value == 80

    def test_verbose_propagates_to_worker(self, running_worker):
        # Arrange
        worker = running_worker
        # Act
        value = worker.verbose
        # Assert
        assert value is False

    def test_monitor_id_propagates_to_worker(self, running_worker):
        # Arrange
        worker = running_worker
        # Act
        value = worker.monitor
        # Assert
        assert value == 2

    def test_capture_all_propagates_to_worker(self, running_worker):
        # Arrange
        worker = running_worker
        # Act
        value = worker.capture_all
        # Assert
        assert value is True


class TestSessionCallbacks:
    """Test Session forwards callbacks to the worker."""

    def test_on_capture_callback_reaches_worker(self):
        # Arrange
        from scitex_capture.session import Session

        captures = []
        callback = lambda p: captures.append(p)
        with tempfile.TemporaryDirectory() as tmpdir:
            # Act
            with Session(output_dir=tmpdir, on_capture=callback, verbose=False) as sess:
                forwarded = sess.worker.on_capture
            # Assert
            assert forwarded is callback

    def test_on_error_callback_reaches_worker(self):
        # Arrange
        from scitex_capture.session import Session

        errors = []
        callback = lambda e: errors.append(e)
        with tempfile.TemporaryDirectory() as tmpdir:
            # Act
            with Session(output_dir=tmpdir, on_error=callback, verbose=False) as sess:
                forwarded = sess.worker.on_error
            # Assert
            assert forwarded is callback


class TestSessionExceptionHandling:
    """Test Session behavior when the body raises."""

    def test_exception_in_context_still_stops_worker(self):
        # Arrange
        from scitex_capture.session import Session

        with tempfile.TemporaryDirectory() as tmpdir:
            sess = Session(output_dir=tmpdir, verbose=False)
            worker_ref = None
            # Act
            try:
                with sess:
                    worker_ref = sess.worker
                    raise ValueError("Test exception")
            except ValueError:
                pass
            # Assert
            assert worker_ref.running is False


class TestSessionFactoryFunction:
    """Test session() factory function."""

    def test_session_returns_session_instance(self):
        # Arrange
        from scitex_capture.session import Session, session

        # Act
        result = session()
        # Assert
        assert isinstance(result, Session)

    def test_session_factory_works_as_context_manager(self):
        # Arrange
        from scitex_capture.session import session

        with tempfile.TemporaryDirectory() as tmpdir:
            # Act
            with session(output_dir=tmpdir, verbose=False) as sess:
                running_inside = sess.worker.running
            # Assert
            assert running_inside is True


class TestSessionFactoryKwargs:
    """session() must forward every kwarg to Session.__init__."""

    @pytest.fixture
    def factory_session(self):
        from scitex_capture.session import session

        with tempfile.TemporaryDirectory() as tmpdir:
            yield (
                session(
                    output_dir=tmpdir,
                    interval=2.0,
                    jpeg=False,
                    quality=75,
                    verbose=False,
                    monitor_id=3,
                    capture_all=True,
                ),
                tmpdir,
            )

    def test_factory_forwards_output_dir(self, factory_session):
        # Arrange
        sess, tmpdir = factory_session
        # Act
        value = sess.output_dir
        # Assert
        assert value == tmpdir

    def test_factory_forwards_interval(self, factory_session):
        # Arrange
        sess, _ = factory_session
        # Act
        value = sess.interval
        # Assert
        assert value == 2.0

    def test_factory_forwards_jpeg(self, factory_session):
        # Arrange
        sess, _ = factory_session
        # Act
        value = sess.jpeg
        # Assert
        assert value is False

    def test_factory_forwards_quality(self, factory_session):
        # Arrange
        sess, _ = factory_session
        # Act
        value = sess.quality
        # Assert
        assert value == 75

    def test_factory_forwards_monitor_id(self, factory_session):
        # Arrange
        sess, _ = factory_session
        # Act
        value = sess.monitor_id
        # Assert
        assert value == 3

    def test_factory_forwards_capture_all(self, factory_session):
        # Arrange
        sess, _ = factory_session
        # Act
        value = sess.capture_all
        # Assert
        assert value is True


class TestModuleExports:
    """Test module exports."""

    def test_session_class_is_importable(self):
        # Arrange
        # Act
        from scitex_capture.session import Session

        # Assert
        assert Session is not None

    def test_session_function_is_callable(self):
        # Arrange
        # Act
        from scitex_capture.session import session

        # Assert
        assert callable(session)

    def test_session_accessible_from_package_root(self):
        # Arrange
        # Act
        from scitex_capture import session

        # Assert
        assert callable(session)


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
