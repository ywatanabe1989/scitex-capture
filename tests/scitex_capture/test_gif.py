#!/usr/bin/env python3
"""Tests for scitex_capture.gif module.

Tests GIF creation functionality with *real* PIL images written to
TemporaryDirectories:
- GifCreator class methods
- create_gif_from_files()
- create_gif_from_session()
- create_gif_from_pattern()
- Session detection

The "PIL not installed" branch is exercised by a real subprocess whose
PYTHONPATH contains a stub ``PIL`` package that raises ImportError — no
mocking of ``sys.modules``.
"""

import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import pytest


def _make_jpg(path, size=(100, 100), color=(255, 0, 0)):
    """Write a real JPEG to ``path`` (importorskip-gated on PIL)."""
    Image = pytest.importorskip("PIL.Image")
    Image.new("RGB", size, color=color).save(path, "JPEG")
    return path


class TestGifCreatorInit:
    def test_gifcreator_instantiates_without_error(self):
        # Arrange
        from scitex_capture.gif import GifCreator

        # Act
        creator = GifCreator()
        # Assert
        assert creator is not None


class TestCreateGifFromFiles:
    """Behavioural tests for create_gif_from_files with real images."""

    @pytest.fixture
    def three_frames(self, tmp_path):
        paths = []
        for i in range(3):
            p = tmp_path / f"frame_{i}.jpg"
            _make_jpg(p, color=(255 - i * 50, i * 50, 0))
            paths.append(str(p))
        return paths

    def test_valid_images_return_a_path(self, three_frames, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        out = str(tmp_path / "output.gif")
        # Act
        result = GifCreator().create_gif_from_files(
            image_paths=three_frames, output_path=out
        )
        # Assert
        assert result is not None

    def test_valid_images_write_the_gif_to_disk(self, three_frames, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        out = str(tmp_path / "output.gif")
        # Act
        result = GifCreator().create_gif_from_files(
            image_paths=three_frames, output_path=out
        )
        # Assert
        assert os.path.exists(result)

    def test_valid_images_return_path_with_gif_suffix(self, three_frames, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        out = str(tmp_path / "output.gif")
        # Act
        result = GifCreator().create_gif_from_files(
            image_paths=three_frames, output_path=out
        )
        # Assert
        assert result.endswith(".gif")

    def test_empty_paths_return_none(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        out = str(tmp_path / "output.gif")
        # Act
        result = GifCreator().create_gif_from_files(image_paths=[], output_path=out)
        # Assert
        assert result is None

    def test_nonexistent_paths_return_none(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        out = str(tmp_path / "output.gif")
        # Act
        result = GifCreator().create_gif_from_files(
            image_paths=["/nonexistent/a.jpg", "/nonexistent/b.jpg"],
            output_path=out,
        )
        # Assert
        assert result is None

    def test_custom_duration_returns_a_path(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        paths = [
            _make_jpg(tmp_path / f"f{i}.jpg", size=(50, 50), color="blue")
            for i in range(2)
        ]
        out = str(tmp_path / "output.gif")
        # Act
        result = GifCreator().create_gif_from_files(
            image_paths=[str(p) for p in paths], output_path=out, duration=1.0
        )
        # Assert
        assert result is not None

    def test_mismatched_sizes_are_handled(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        img1 = _make_jpg(tmp_path / "f1.jpg", size=(100, 100), color="red")
        img2 = _make_jpg(tmp_path / "f2.jpg", size=(200, 200), color="blue")
        out = str(tmp_path / "output.gif")
        # Act
        result = GifCreator().create_gif_from_files(
            image_paths=[str(img1), str(img2)], output_path=out
        )
        # Assert
        assert result is not None

    def test_creates_missing_parent_directory(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        img = _make_jpg(tmp_path / "frame.jpg", size=(50, 50), color="green")
        out = str(tmp_path / "nested" / "deep" / "output.gif")
        # Act
        GifCreator().create_gif_from_files(image_paths=[str(img)], output_path=out)
        # Assert
        assert os.path.isdir(os.path.dirname(out))


class TestCreateGifFromSession:
    """Behavioural tests for create_gif_from_session."""

    def _make_session_frames(self, tmp_path, session_id, count, ext="jpg"):
        for i in range(count):
            name = f"{session_id}_{i:04d}_120000000.{ext}"
            _make_jpg(tmp_path / name, color="red")

    def test_no_matching_files_returns_none(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        # Act
        result = GifCreator().create_gif_from_session(
            session_id="20250104_120000", screenshot_dir=str(tmp_path)
        )
        # Assert
        assert result is None

    def test_matching_files_return_a_path(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        session_id = "20250104_120000"
        self._make_session_frames(tmp_path, session_id, 3)
        # Act
        result = GifCreator().create_gif_from_session(
            session_id=session_id, screenshot_dir=str(tmp_path)
        )
        # Assert
        assert result is not None

    def test_matching_files_embed_session_id_in_output(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        session_id = "20250104_120000"
        self._make_session_frames(tmp_path, session_id, 3)
        # Act
        result = GifCreator().create_gif_from_session(
            session_id=session_id, screenshot_dir=str(tmp_path)
        )
        # Assert
        assert session_id in result

    def test_png_only_session_falls_back_to_png(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        session_id = "20250104_130000"
        for i in range(2):
            name = f"{session_id}_{i:04d}_130000000.png"
            pytest.importorskip("PIL.Image")
            from PIL import Image

            Image.new("RGB", (100, 100), "blue").save(tmp_path / name)
        # Act
        result = GifCreator().create_gif_from_session(
            session_id=session_id, screenshot_dir=str(tmp_path)
        )
        # Assert
        assert result is not None

    def test_max_frames_limit_still_returns_a_path(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        session_id = "20250104_140000"
        self._make_session_frames(tmp_path, session_id, 10)
        # Act
        result = GifCreator().create_gif_from_session(
            session_id=session_id, screenshot_dir=str(tmp_path), max_frames=3
        )
        # Assert
        assert result is not None


class TestCreateGifFromPattern:
    """Behavioural tests for create_gif_from_pattern."""

    def test_no_matches_returns_none(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        pattern = str(tmp_path / "nonexistent_*.jpg")
        # Act
        result = GifCreator().create_gif_from_pattern(pattern=pattern)
        # Assert
        assert result is None

    def test_matches_return_a_path(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        for i in range(3):
            _make_jpg(tmp_path / f"screenshot_{i}.jpg", color="purple")
        pattern = str(tmp_path / "screenshot_*.jpg")
        out = str(tmp_path / "result.gif")
        # Act
        result = GifCreator().create_gif_from_pattern(pattern=pattern, output_path=out)
        # Assert
        assert result is not None

    def test_matches_write_the_gif_to_disk(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        for i in range(3):
            _make_jpg(tmp_path / f"screenshot_{i}.jpg", color="purple")
        pattern = str(tmp_path / "screenshot_*.jpg")
        out = str(tmp_path / "result.gif")
        # Act
        result = GifCreator().create_gif_from_pattern(pattern=pattern, output_path=out)
        # Assert
        assert os.path.exists(result)

    def test_auto_output_path_returns_a_path(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        _make_jpg(tmp_path / "test_image.jpg", size=(50, 50), color="yellow")
        pattern = str(tmp_path / "test_*.jpg")
        # Act
        result = GifCreator().create_gif_from_pattern(pattern=pattern)
        # Assert
        assert result is not None

    def test_auto_output_path_uses_gif_summary_prefix(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        _make_jpg(tmp_path / "test_image.jpg", size=(50, 50), color="yellow")
        pattern = str(tmp_path / "test_*.jpg")
        # Act
        result = GifCreator().create_gif_from_pattern(pattern=pattern)
        # Assert
        assert "gif_summary_" in result

    def test_max_frames_limit_still_returns_a_path(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        for i in range(10):
            _make_jpg(tmp_path / f"img_{i:02d}.jpg", size=(50, 50), color="orange")
        pattern = str(tmp_path / "img_*.jpg")
        out = str(tmp_path / "limited.gif")
        # Act
        result = GifCreator().create_gif_from_pattern(
            pattern=pattern, output_path=out, max_frames=3
        )
        # Assert
        assert result is not None


class TestGetRecentSessions:
    """Behavioural tests for get_recent_sessions."""

    def test_empty_dir_returns_empty_list(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        # Act
        result = GifCreator().get_recent_sessions(screenshot_dir=str(tmp_path))
        # Assert
        assert result == []

    def test_nonexistent_dir_returns_empty_list(self):
        # Arrange
        from scitex_capture.gif import GifCreator

        # Act
        result = GifCreator().get_recent_sessions(screenshot_dir="/nonexistent/path")
        # Assert
        assert result == []

    def test_two_sessions_are_both_detected(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        s1, s2 = "20250101_100000", "20250102_110000"
        Path(tmp_path / f"{s1}_0001_100000000.jpg").touch()
        Path(tmp_path / f"{s1}_0002_100001000.jpg").touch()
        Path(tmp_path / f"{s2}_0001_110000000.jpg").touch()
        # Act
        result = GifCreator().get_recent_sessions(screenshot_dir=str(tmp_path))
        # Assert
        assert set(result) == {s1, s2}

    def test_sessions_sorted_newest_first(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        sessions = ["20250101_100000", "20250103_100000", "20250102_100000"]
        for sess in sessions:
            Path(tmp_path / f"{sess}_0001_100000000.jpg").touch()
        # Act
        result = GifCreator().get_recent_sessions(screenshot_dir=str(tmp_path))
        # Assert
        assert result == sorted(sessions, reverse=True)


class TestCreateGifFromRecentSession:
    """Behavioural tests for create_gif_from_recent_session."""

    def test_no_sessions_returns_none(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        # Act
        result = GifCreator().create_gif_from_recent_session(
            screenshot_dir=str(tmp_path)
        )
        # Assert
        assert result is None

    def test_with_session_returns_a_path(self, tmp_path):
        # Arrange
        from scitex_capture.gif import GifCreator

        session_id = "20250104_150000"
        for i in range(3):
            _make_jpg(tmp_path / f"{session_id}_{i:04d}_150000000.jpg", color="cyan")
        # Act
        result = GifCreator().create_gif_from_recent_session(
            screenshot_dir=str(tmp_path)
        )
        # Assert
        assert result is not None


class TestConvenienceFunctions:
    """Module-level convenience wrappers return None on no input."""

    def test_create_gif_from_session_function_returns_none(self, tmp_path):
        # Arrange
        from scitex_capture.gif import create_gif_from_session

        # Act
        result = create_gif_from_session(
            session_id="nonexistent", screenshot_dir=str(tmp_path)
        )
        # Assert
        assert result is None

    def test_create_gif_from_files_function_returns_none(self, tmp_path):
        # Arrange
        from scitex_capture.gif import create_gif_from_files

        out = str(tmp_path / "output.gif")
        # Act
        result = create_gif_from_files(image_paths=[], output_path=out)
        # Assert
        assert result is None

    def test_create_gif_from_pattern_function_returns_none(self, tmp_path):
        # Arrange
        from scitex_capture.gif import create_gif_from_pattern

        pattern = str(tmp_path / "*.jpg")
        # Act
        result = create_gif_from_pattern(pattern=pattern)
        # Assert
        assert result is None

    def test_create_gif_from_latest_session_function_returns_none(self, tmp_path):
        # Arrange
        from scitex_capture.gif import create_gif_from_latest_session

        # Act
        result = create_gif_from_latest_session(screenshot_dir=str(tmp_path))
        # Assert
        assert result is None


class TestModuleExports:
    """Test module exports are importable and callable."""

    def test_gifcreator_is_importable(self):
        # Arrange
        # Act
        from scitex_capture.gif import GifCreator

        # Assert
        assert GifCreator is not None

    def test_create_gif_from_session_is_callable(self):
        # Arrange
        # Act
        from scitex_capture.gif import create_gif_from_session

        # Assert
        assert callable(create_gif_from_session)

    def test_create_gif_from_files_is_callable(self):
        # Arrange
        # Act
        from scitex_capture.gif import create_gif_from_files

        # Assert
        assert callable(create_gif_from_files)

    def test_create_gif_from_pattern_is_callable(self):
        # Arrange
        # Act
        from scitex_capture.gif import create_gif_from_pattern

        # Assert
        assert callable(create_gif_from_pattern)

    def test_create_gif_from_latest_session_is_callable(self):
        # Arrange
        # Act
        from scitex_capture.gif import create_gif_from_latest_session

        # Assert
        assert callable(create_gif_from_latest_session)

    def test_create_gif_from_session_accessible_from_package_root(self):
        # Arrange
        # Act
        from scitex_capture import create_gif_from_session

        # Assert
        assert callable(create_gif_from_session)


class TestPILNotAvailable:
    """The 'PIL not installed' branch must return None.

    Exercised by a real subprocess whose PYTHONPATH front-loads a stub
    ``PIL`` package that raises ImportError on import — the real
    ``except ImportError`` branch in gif.create_gif_from_files runs.
    """

    def test_missing_pil_makes_create_gif_from_files_return_none(self, tmp_path):
        # Arrange
        stub_root = tmp_path / "stub"
        (stub_root / "PIL").mkdir(parents=True)
        (stub_root / "PIL" / "__init__.py").write_text(
            'raise ImportError("PIL blocked for test")\n'
        )
        runner = tmp_path / "run.py"
        runner.write_text(
            textwrap.dedent(
                """
                import os, tempfile
                from scitex_capture.gif import create_gif_from_files
                with tempfile.TemporaryDirectory() as d:
                    out = os.path.join(d, "out.gif")
                    r = create_gif_from_files(
                        image_paths=["/some/path.jpg"], output_path=out
                    )
                    print("RESULT_IS_NONE", r is None)
                """
            )
        )
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join([str(stub_root), env.get("PYTHONPATH", "")])
        # Act
        proc = subprocess.run(
            [sys.executable, str(runner)],
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )
        # Assert
        assert "RESULT_IS_NONE True" in proc.stdout


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
