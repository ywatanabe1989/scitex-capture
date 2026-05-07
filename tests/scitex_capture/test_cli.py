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


def test_main_help_exits_zero():
    result = CliRunner().invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "scitex-capture" in result.output


def test_main_version_flag():
    result = CliRunner().invoke(main, ["--version"])
    assert result.exit_code == 0


def test_help_recursive_lists_subcommands():
    result = CliRunner().invoke(main, ["--help-recursive"])
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
    result = CliRunner().invoke(main, ["list-windows", "--help"])
    assert result.exit_code == 0


def test_show_info_help():
    result = CliRunner().invoke(main, ["show-info", "--help"])
    assert result.exit_code == 0


def test_make_gif_help():
    result = CliRunner().invoke(main, ["make-gif", "--help"])
    assert result.exit_code == 0


def test_unknown_subcommand_rejected():
    # Unknown subcommand → exit 2 (Click's "no such command" usage error).
    result = CliRunner().invoke(main, ["bogus-subcommand"])
    assert result.exit_code != 0
