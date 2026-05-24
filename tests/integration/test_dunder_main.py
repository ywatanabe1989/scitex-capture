#!/usr/bin/env python3
"""Tests for scitex_capture.__main__ module.

Tests the entry point for `python -m scitex_capture`:
- Module imports
- Main function accessibility
- Module execution as a real subprocess
"""

import subprocess
import sys

import pytest


class TestModuleImports:
    """Test module import functionality."""

    def test_dunder_main_module_is_importable(self):
        # Arrange
        # Act
        from scitex_capture import __main__

        # Assert
        assert __main__ is not None

    def test_main_callable_is_accessible(self):
        # Arrange
        # Act
        from scitex_capture.__main__ import main

        # Assert
        assert callable(main)

    def test_main_is_the_cli_main_object(self):
        # Arrange
        from scitex_capture.__main__ import main

        # Act
        from scitex_capture.cli import main as cli_main

        # Assert
        assert main is cli_main


class TestModuleExecution:
    """Test module execution as a script via a real subprocess."""

    def _run_module(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "scitex_capture", *args],
            capture_output=True,
            text=True,
            timeout=15,
        )

    def test_help_invocation_exits_zero(self):
        # Arrange
        # Act
        result = self._run_module("--help")
        # Assert
        assert result.returncode == 0

    def test_help_invocation_emits_usage_or_help_text(self):
        # Arrange
        # Act
        result = self._run_module("--help")
        # Assert
        out = result.stdout.lower()
        assert "usage" in out or "help" in out


class TestModuleIntegration:
    """Test module integration with the CLI subcommands."""

    def _run_module(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "scitex_capture", *args],
            capture_output=True,
            text=True,
            timeout=15,
        )

    def test_help_text_lists_list_windows_subcommand(self):
        # Arrange
        # Act
        result = self._run_module("--help")
        # Assert
        assert "list-windows" in result.stdout.lower()

    def test_help_text_lists_show_info_subcommand(self):
        # Arrange
        # Act
        result = self._run_module("--help")
        # Assert
        assert "show-info" in result.stdout.lower()

    def test_list_windows_help_via_module_exits_zero(self):
        # Arrange
        # Act
        result = self._run_module("list-windows", "--help")
        # Assert
        assert result.returncode == 0

    def test_show_info_help_via_module_exits_zero(self):
        # Arrange
        # Act
        result = self._run_module("show-info", "--help")
        # Assert
        assert result.returncode == 0


class TestModuleAttributes:
    """Test module-level attributes."""

    def test_module_exposes_file_attribute(self):
        # Arrange
        # Act
        from scitex_capture import __main__

        # Assert
        assert hasattr(__main__, "__FILE__")

    def test_module_exposes_dir_attribute(self):
        # Arrange
        # Act
        from scitex_capture import __main__

        # Assert
        assert hasattr(__main__, "__DIR__")


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__)])
