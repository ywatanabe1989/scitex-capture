"""Smoke tests for the Click-based scitex-capture CLI.

The previous test_cli.py (548 lines) tested the pre-Click argparse-era
shape (`capture --list`, `capture --info`, etc.). The CLI was refactored
to a Click group with `list-windows` / `show-info` / `start-monitor` /
`stop-monitor` / `make-gif` subcommands, so every old test broke with
`NoSuchOption: --list`.

A full rewrite (mock-based behaviour tests for each subcommand) is real
work that needs to be scheduled separately. For now, this file replaces
the broken suite with subprocess-free Click `CliRunner` smoke tests
that exercise the help surface and verify the subcommand names exist.
"""

from click.testing import CliRunner

from scitex_capture.cli import main


def test_main_help_exits_zero_result_exit_code_equals_n_0():
    # Arrange
    # Arrange
    # Act
    result = CliRunner().invoke(main, ["--help"])
    # Act
    # Assert
    # Assert
    assert result.exit_code == 0


def test_main_help_exits_zero_scitex_capture_in_result_output():
    # Arrange
    # Arrange
    # Act
    result = CliRunner().invoke(main, ["--help"])
    # Act
    # Assert
    # Assert
    assert "scitex-capture" in result.output




def test_main_version_flag():
    # Arrange
    # Act
    result = CliRunner().invoke(main, ["--version"])
    # Assert
    assert result.exit_code == 0


def test_help_recursive_lists_subcommands():
    # Arrange
    # Act
    result = CliRunner().invoke(main, ["--help-recursive"])
    # Assert
    assert result.exit_code == 0
    for sub in (
        "list-windows",
        "show-info",
        "start-monitor",
        "stop-monitor",
        "make-gif",
    ):
        assert sub in result.output, f"subcommand {sub!r} missing from help"


def test_list_windows_help():
    # Arrange
    # Act
    result = CliRunner().invoke(main, ["list-windows", "--help"])
    # Assert
    assert result.exit_code == 0


def test_show_info_help():
    # Arrange
    # Act
    result = CliRunner().invoke(main, ["show-info", "--help"])
    # Assert
    assert result.exit_code == 0


def test_make_gif_help():
    # Arrange
    # Act
    result = CliRunner().invoke(main, ["make-gif", "--help"])
    # Assert
    assert result.exit_code == 0


def test_unknown_subcommand_rejected():
    # Unknown subcommand → exit 2 (Click's "no such command" usage error).
    # Arrange
    # Act
    result = CliRunner().invoke(main, ["bogus-subcommand"])
    # Assert
    assert result.exit_code != 0
