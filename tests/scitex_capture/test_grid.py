#!/usr/bin/env python3
"""Tests for scitex_capture.grid module."""

import importlib

import pytest


class TestGridModule:
    """Smoke tests for the grid overlay module."""

    def test_module_importable_returns_module_object(self):
        # Arrange
        module_name = "scitex_capture.grid"
        # Act
        mod = importlib.import_module(module_name)
        # Assert
        assert mod is not None

    def test_public_helpers_are_all_callable(self):
        # Arrange
        from scitex_capture import grid

        expected = (
            "draw_grid_overlay",
            "add_monitor_info_overlay",
            "draw_cursor_overlay",
            "get_display_info",
        )
        # Act
        callables = {n for n in expected if callable(getattr(grid, n, None))}
        # Assert
        assert callables == set(expected)

    def test_all_lists_documented_public_helpers(self):
        # Arrange
        from scitex_capture import grid

        expected = {
            "draw_grid_overlay",
            "add_monitor_info_overlay",
            "draw_cursor_overlay",
            "get_display_info",
        }
        # Act
        exported = set(grid.__all__)
        # Assert
        assert exported >= expected


@pytest.fixture
def black_png(tmp_path):
    """A real 300x200 black PNG written to tmp_path."""
    Image = pytest.importorskip("PIL.Image")
    src = tmp_path / "src.png"
    Image.new("RGB", (300, 200), color=(0, 0, 0)).save(src)
    return src


class TestDrawGridOverlay:
    """Behavioural tests for draw_grid_overlay against a real PNG."""

    def test_returns_path_with_grid_suffix(self, black_png):
        # Arrange
        from scitex_capture.grid import draw_grid_overlay

        # Act
        out = draw_grid_overlay(str(black_png), grid_spacing=50, show_coordinates=False)
        # Assert
        assert out.endswith("_grid.png")

    def test_writes_output_file_to_disk(self, black_png, tmp_path):
        # Arrange
        from scitex_capture.grid import draw_grid_overlay

        # Act
        draw_grid_overlay(str(black_png), grid_spacing=50, show_coordinates=False)
        # Assert
        assert (tmp_path / "src_grid.png").is_file()

    def test_writes_non_empty_output_file(self, black_png, tmp_path):
        # Arrange
        from scitex_capture.grid import draw_grid_overlay

        # Act
        draw_grid_overlay(str(black_png), grid_spacing=50, show_coordinates=False)
        # Assert
        assert (tmp_path / "src_grid.png").stat().st_size > 0


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__)])
