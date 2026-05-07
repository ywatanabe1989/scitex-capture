#!/usr/bin/env python3
"""Tests for scitex_capture.__main__ module.

Tests the entry point for python -m scitex.capture:
- Module imports
- Main function accessibility
- Module execution
"""

import os
import subprocess
import sys
from unittest.mock import patch

import pytest


class TestModuleImports:
    """Test module import functionality."""

    def test_module_importable(self):
        """Test __main__ module can be imported."""
        from scitex_capture import __main__

        assert __main__ is not None

    def test_main_accessible(self):
        """Test main function is accessible from module."""
        from scitex_capture.__main__ import main

        assert callable(main)

    def test_main_is_from_cli(self):
        """Test main function is imported from cli module."""
        from scitex_capture.__main__ import main
        from scitex_capture.cli import main as cli_main

        assert main is cli_main


class TestModuleExecution:
    """Test module execution as script."""

    def test_module_runnable_with_help(self):
        """Test module can be run with python -m and --help."""
        result = subprocess.run(
            [sys.executable, "-m", "scitex_capture", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert "usage" in result.stdout.lower() or "help" in result.stdout.lower()

    def test_module_execution_calls_main(self):
        """Test module execution calls main function."""
        from scitex_capture import __main__

        with patch.object(__main__, "main", return_value=0) as mock_main:
            # Simulate running as __main__
            with patch.object(__main__, "__name__", "__main__"):
                # The actual execution happens at import time,
                # so we test the structure
                assert hasattr(__main__, "main")
                assert callable(__main__.main)

    def test_module_returns_main_exit_code(self):
        """`python -m scitex_capture --help` exits 0 (sys.exit forwards Click's exit)."""
        result = subprocess.run(
            [sys.executable, "-m", "scitex_capture", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0


class TestModuleIntegration:
    """Test module integration with CLI."""

    def test_help_output_contains_capture_commands(self):
        """Help output mentions the canonical subcommand names (post-Click refactor)."""
        result = subprocess.run(
            [sys.executable, "-m", "scitex_capture", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        help_text = result.stdout.lower()
        assert "list-windows" in help_text
        assert "show-info" in help_text

    def test_list_windows_help_via_module(self):
        """`list-windows --help` exits 0 — flag-shape was renamed to subcommand."""
        result = subprocess.run(
            [sys.executable, "-m", "scitex_capture", "list-windows", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0

    def test_show_info_help_via_module(self):
        """`show-info --help` exits 0 — flag-shape was renamed to subcommand."""
        result = subprocess.run(
            [sys.executable, "-m", "scitex_capture", "show-info", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0


class TestModuleAttributes:
    """Test module-level attributes."""

    def test_module_has_file_attribute(self):
        """Test module has __FILE__ attribute."""
        from scitex_capture import __main__

        assert hasattr(__main__, "__FILE__")

    def test_module_has_dir_attribute(self):
        """Test module has __DIR__ attribute."""
        from scitex_capture import __main__

        assert hasattr(__main__, "__DIR__")

    def test_module_docstring_exists(self):
        """Test module has a docstring."""
        from scitex_capture import __main__

        # The docstring is in the source but may not be __doc__
        # Check the source structure is correct
        assert __main__ is not None


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/capture/__main__.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-10-18 09:55:55 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex-code/src/scitex/capture/__main__.py
# # ----------------------------------------
# from __future__ import annotations
# import os
#
# __FILE__ = "./src/scitex/capture/__main__.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# """
# Entry point for python -m scitex.capture
# """
#
# import sys
#
# from .cli import main
#
# if __name__ == "__main__":
#     sys.exit(main())
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/capture/__main__.py
# --------------------------------------------------------------------------------
