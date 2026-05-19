#!/usr/bin/env python3
"""Tests for scitex_capture.grid module."""

import importlib

import pytest


class TestGridModule:
    """Smoke tests for the grid overlay module."""

    def test_module_importable_mod_is_not_none(self):
        """grid module imports cleanly."""
        # Arrange
        # Act
        mod = importlib.import_module("scitex_capture.grid")
        # Assert
        assert mod is not None

    def test_public_api_exposed(self):
        """Documented helpers are exported as callables."""
        # Arrange
        # Act
        # Assert
        from scitex_capture import grid

        for name in (
            "draw_grid_overlay",
            "add_monitor_info_overlay",
            "draw_cursor_overlay",
            "get_display_info",
        ):
            assert hasattr(grid, name), f"missing {name}"
            assert callable(getattr(grid, name)), f"{name} not callable"

    def test_all_lists_public_helpers(self):
        """__all__ matches the documented public helpers."""
        # Arrange
        # Act
        from scitex_capture import grid

        # Assert
        assert set(grid.__all__) >= {
            "draw_grid_overlay",
            "add_monitor_info_overlay",
            "draw_cursor_overlay",
            "get_display_info",
        }


class TestDrawGridOverlay:
    """Behavioural tests for draw_grid_overlay."""

    def test_draws_grid_on_image_out_endswith_grid_png(self, tmp_path):
        # Arrange
        # Arrange
        Image = pytest.importorskip("PIL.Image")
        from scitex_capture.grid import draw_grid_overlay
        src = tmp_path / "src.png"
        Image.new("RGB", (300, 200), color=(0, 0, 0)).save(src)
        # Act
        out = draw_grid_overlay(str(src), grid_spacing=50, show_coordinates=False)
        # Act
        # Assert
        # Assert
        assert out.endswith("_grid.png")

    def test_draws_grid_on_image_out_path_is_file(self, tmp_path):
        # Arrange
        # Arrange
        Image = pytest.importorskip("PIL.Image")
        from scitex_capture.grid import draw_grid_overlay
        src = tmp_path / "src.png"
        Image.new("RGB", (300, 200), color=(0, 0, 0)).save(src)
        # Act
        out = draw_grid_overlay(str(src), grid_spacing=50, show_coordinates=False)
        # Assert
        assert out.endswith("_grid.png")
        out_path = tmp_path / "src_grid.png"
        # Act
        # Assert
        assert out_path.is_file()

    def test_draws_grid_on_image_out_path_stat_st_size_0(self, tmp_path):
        # Arrange
        # Arrange
        Image = pytest.importorskip("PIL.Image")
        from scitex_capture.grid import draw_grid_overlay
        src = tmp_path / "src.png"
        Image.new("RGB", (300, 200), color=(0, 0, 0)).save(src)
        # Act
        out = draw_grid_overlay(str(src), grid_spacing=50, show_coordinates=False)
        # Assert
        assert out.endswith("_grid.png")
        out_path = tmp_path / "src_grid.png"
        # Act
        # Assert
        assert out_path.stat().st_size > 0



if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__)])
