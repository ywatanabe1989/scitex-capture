#!/usr/bin/env python3
"""Tests for scitex_capture.grid module."""

import importlib

import pytest


class TestGridModule:
    """Smoke tests for the grid overlay module."""

    def test_module_importable(self):
        """grid module imports cleanly."""
        mod = importlib.import_module("scitex_capture.grid")
        assert mod is not None

    def test_public_api_exposed(self):
        """Documented helpers are exported as callables."""
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
        from scitex_capture import grid

        assert set(grid.__all__) >= {
            "draw_grid_overlay",
            "add_monitor_info_overlay",
            "draw_cursor_overlay",
            "get_display_info",
        }


class TestDrawGridOverlay:
    """Behavioural tests for draw_grid_overlay."""

    def test_draws_grid_on_image(self, tmp_path):
        """Produces a non-empty output image with a grid drawn."""
        Image = pytest.importorskip("PIL.Image")
        from scitex_capture.grid import draw_grid_overlay

        src = tmp_path / "src.png"
        Image.new("RGB", (300, 200), color=(0, 0, 0)).save(src)

        out = draw_grid_overlay(str(src), grid_spacing=50, show_coordinates=False)

        assert out.endswith("_grid.png")
        out_path = tmp_path / "src_grid.png"
        assert out_path.is_file()
        assert out_path.stat().st_size > 0


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__)])
