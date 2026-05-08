#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scitex-capture CLI — AI's Camera (Click)."""

from __future__ import annotations

import json
import sys

import click


def _get_version() -> str:
    try:
        from importlib.metadata import version

        return version("scitex-capture")
    except Exception:
        return "0.0.0"


def _print_help_recursive(ctx: click.Context, _param, value):
    if not value or ctx.resilient_parsing:
        return
    cmd = ctx.command
    click.echo(cmd.get_help(ctx))
    if isinstance(cmd, click.Group):
        for name in sorted(cmd.commands):
            sub = cmd.commands[name]
            sub_ctx = click.Context(sub, info_name=name, parent=ctx)
            click.echo("\n---\n")
            click.echo(sub.get_help(sub_ctx))
    ctx.exit(0)


@click.group(
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("message", required=False)
@click.option("--all", "all_monitors", is_flag=True, help="Capture all monitors.")
@click.option("--app", default=None, help="App name to capture (e.g., chrome).")
@click.option("--url", default=None, help="URL to capture (e.g., 127.0.0.1:8000).")
@click.option("--monitor", type=int, default=0, help="Monitor ID (0-based).")
@click.option("--quality", type=int, default=85, help="JPEG quality (1-100).")
@click.option("-o", "--output", default=None, help="Output path.")
@click.option("-q", "--quiet", is_flag=True, help="Quiet mode.")
@click.version_option(_get_version(), "-V", "--version", prog_name="scitex-capture")
@click.option(
    "--help-recursive",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_print_help_recursive,
    help="Show help for the root and every subcommand.",
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    default=False,
    help="Emit machine-readable JSON output where supported.",
)
@click.pass_context
def main(
    ctx, message, all_monitors, app, url, monitor, quality, output, quiet, as_json
):
    """scitex-capture — AI's Camera: capture screenshots from anywhere.

    \b
    Configuration precedence (highest -> lowest):
      1. Explicit CLI flags
      2. ./config.yaml (project-local)
      3. $SCITEX_CAPTURE_CONFIG (path to a YAML file)
      4. ~/.scitex/capture/config.yaml (user-wide)
      5. Built-in defaults

    \b
    Default action: capture a screenshot.

    \b
    Example:
        $ scitex-capture                            # capture current screen
        $ scitex-capture --all                      # all monitors
        $ scitex-capture --app chrome
        $ scitex-capture "release-shot"             # message → filename
        $ scitex-capture list-windows
        $ scitex-capture start-monitor --interval 2
        $ scitex-capture make-gif
    """
    ctx.ensure_object(dict)
    ctx.obj["as_json"] = as_json
    if ctx.invoked_subcommand is not None:
        return
    # Default: snap a screenshot.
    import scitex_capture as capture

    verbose = not quiet
    try:
        path = capture.snap(
            message=message,
            path=output,
            quality=quality,
            monitor_id=monitor,
            all=all_monitors,
            app=app,
            url=url,
            verbose=verbose,
        )
        if path:
            if not quiet:
                if as_json:
                    click.echo(json.dumps({"path": str(path)}))
                else:
                    click.echo(f"\u2705 {path}")
            ctx.exit(0)
        else:
            click.echo("\u274c Screenshot failed", err=True)
            ctx.exit(1)
    except KeyboardInterrupt:
        click.echo("\n\u26a0\ufe0f  Interrupted", err=True)
        ctx.exit(130)
    except Exception as e:
        click.echo(f"\u274c Error: {e}", err=True)
        ctx.exit(1)


@main.command("list-windows")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def list_windows(as_json):
    """List visible application windows that can be captured.

    \b
    Example:
        $ scitex-capture list-windows
        $ scitex-capture list-windows --json
    """
    import scitex_capture as capture

    info = capture.get_info()
    windows = info.get("Windows", {}).get("Details", [])
    if as_json:
        click.echo(json.dumps({"windows": windows}, indent=2))
        return
    click.echo(f"\n\U0001f4f1 Visible Windows ({len(windows)}):")
    click.echo("=" * 60)
    for i, win in enumerate(windows, 1):
        click.echo(f"{i}. [{win['ProcessName']}] {win['Title']}")
        click.echo(f"   Handle: {win['Handle']} | PID: {win['ProcessId']}")


@main.command("show-info")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def show_info(as_json):
    """Show display information (monitors, windows, virtual desktops).

    \b
    Example:
        $ scitex-capture show-info
        $ scitex-capture show-info --json
    """
    import scitex_capture as capture

    info = capture.get_info()
    if as_json:
        click.echo(json.dumps(info, indent=2))
        return

    monitors = info.get("Monitors", {})
    windows = info.get("Windows", {})
    vd = info.get("VirtualDesktops", {})

    click.echo("\n\U0001f5a5\ufe0f  Display Information")
    click.echo("=" * 60)
    click.echo(f"\n\U0001f4fa Monitors: {monitors.get('Count')}")
    click.echo(f"   Primary: {monitors.get('PrimaryMonitor')}")
    for i, mon in enumerate(monitors.get("Details", [])):
        bounds = mon.get("Bounds", {})
        click.echo(f"\n   Monitor {i}:")
        click.echo(f"     Device: {mon.get('DeviceName')}")
        click.echo(f"     Resolution: {bounds.get('Width')}x{bounds.get('Height')}")
        click.echo(f"     Primary: {mon.get('IsPrimary')}")

    click.echo(f"\n\U0001fa9f Windows: {windows.get('VisibleCount')}")
    click.echo(f"   On current virtual desktop: {len(windows.get('Details', []))}")
    click.echo("\n\U0001f5a5\ufe0f  Virtual Desktops:")
    click.echo(f"   Supported: {vd.get('Supported')}")
    click.echo(f"   Note: {vd.get('Note')}")


@main.command("start-monitor")
@click.option(
    "--interval",
    type=float,
    default=1.0,
    help="Monitoring interval in seconds.",
)
@click.option("--monitor", type=int, default=0, help="Monitor ID (0-based).")
@click.option("--all", "all_monitors", is_flag=True, help="Capture all monitors.")
@click.option("-q", "--quiet", is_flag=True, help="Quiet mode.")
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    default=False,
    help="Skip confirmation (mutating: starts a background loop).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be started without acting.",
)
def start_monitor(interval, monitor, all_monitors, quiet, yes, dry_run):
    """Start periodic screenshot monitoring (foreground loop).

    \b
    Example:
        $ scitex-capture start-monitor --interval 2 --yes
    """
    import scitex_capture as capture

    if dry_run:
        click.echo(
            f"Dry-run: would start monitor (interval={interval}s, monitor={monitor}, "
            f"all_monitors={all_monitors})."
        )
        return
    if not yes:
        click.echo(
            "Refusing to start monitor without --yes/-y "
            f"(interval={interval}s, foreground).",
            err=True,
        )
        sys.exit(2)
    click.echo(f"\U0001f4f8 Starting monitoring (interval: {interval}s)...")
    capture.start(
        interval=interval,
        verbose=not quiet,
        monitor_id=monitor,
        capture_all=all_monitors,
    )
    click.echo(
        "\u2705 Monitoring started. Press Ctrl+C to stop, or run: "
        "scitex-capture stop-monitor"
    )
    click.echo("\U0001f4c1 Saving to: ~/.scitex/capture/")
    try:
        import time

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        capture.stop()
        click.echo("\n\u2705 Monitoring stopped")


@main.command("stop-monitor")
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    default=False,
    help="Skip confirmation (mutating: stops the running monitor).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be stopped without acting.",
)
def stop_monitor(yes, dry_run):
    """Stop a running scitex-capture monitor.

    \b
    Example:
        $ scitex-capture stop-monitor --yes
    """
    import scitex_capture as capture

    if dry_run:
        click.echo("Dry-run: would call capture.stop().")
        return
    if not yes:
        click.echo("Refusing to stop monitor without --yes/-y.", err=True)
        sys.exit(2)
    capture.stop()
    click.echo("\u2705 Monitoring stopped")


@main.command("make-gif")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def make_gif(as_json):
    """Build a GIF from the most recent capture session.

    \b
    Example:
        $ scitex-capture make-gif
    """
    import scitex_capture as capture

    click.echo("\U0001f4f9 Creating GIF from latest session...")
    path = capture.gif()
    if path:
        if as_json:
            click.echo(json.dumps({"path": str(path)}))
        else:
            click.echo(f"\u2705 GIF created: {path}")
        return
    click.echo("\u274c No session found", err=True)
    sys.exit(1)


@main.group()
def mcp():
    """MCP (Model Context Protocol) server management."""


@mcp.command("start")
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    default=False,
    help="Skip confirmation (mutating: starts a long-running server).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would start without launching the server.",
)
def mcp_start(yes, dry_run):
    """Start the scitex-capture MCP server (stdio transport).

    \b
    Example:
        $ scitex-capture mcp start --yes
    """
    if dry_run:
        click.echo("Dry-run: would launch scitex_capture.mcp_server.main()")
        return
    if not yes:
        click.echo("Refusing to start MCP server without --yes/-y.", err=True)
        sys.exit(2)
    click.echo("\U0001f916 Starting scitex.capture MCP server...")
    click.echo("Add to Claude Code settings:")
    click.echo("{")
    click.echo('  "mcpServers": {')
    click.echo('    "scitex-capture": {')
    click.echo('      "command": "scitex-capture",')
    click.echo('      "args": ["mcp", "start"]')
    click.echo("    }")
    click.echo("  }")
    click.echo("}")
    click.echo()

    from .mcp_server import main as mcp_main

    mcp_main()


@mcp.command("list-tools")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def mcp_list_tools(as_json):
    """List MCP tools exposed by scitex-capture.

    \b
    Example:
        $ scitex-capture mcp list-tools
    """
    try:
        from . import mcp_server  # noqa: F401

        tools = ["capture_screenshot", "list_windows", "get_display_info"]
    except Exception:
        tools = []
    if as_json:
        click.echo(json.dumps({"tools": tools}, indent=2))
    else:
        for t in tools:
            click.echo(t)


@main.command("list-python-apis")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def list_python_apis(as_json):
    """List the public Python API surface of scitex_capture.

    \b
    Example:
        $ scitex-capture list-python-apis
        $ scitex-capture list-python-apis --json
    """
    apis = [
        "scitex_capture.snap",
        "scitex_capture.start",
        "scitex_capture.stop",
        "scitex_capture.gif",
        "scitex_capture.get_info",
    ]
    if as_json:
        click.echo(json.dumps({"apis": apis}, indent=2))
    else:
        for a in apis:
            click.echo(a)


_SUBCOMMANDS = {
    "list-windows",
    "show-info",
    "start-monitor",
    "stop-monitor",
    "make-gif",
    "mcp",
    "list-python-apis",
}


def _reorder_argv(argv):
    """Allow ``scitex-capture <MESSAGE> [options...]`` natural ordering."""
    if not argv or "--" in argv:
        return argv
    options, positional, rest = [], None, []
    for i, a in enumerate(argv):
        if positional is not None:
            rest.append(a)
            continue
        if a.startswith("-"):
            options.append(a)
            continue
        if a in _SUBCOMMANDS:
            return argv
        positional = a
    if positional is None:
        return argv
    return options + rest + [positional]


# ----- audit-cli §1a / §4 wiring -------------------------------------------
# §1a: skills group (list / get / install) — required because the package
# ships _skills/scitex-capture/.
@click.group("skills")
def skills_group():
    """Browse / install the agent-facing skills bundled with scitex-capture."""


def _skills_root():
    from pathlib import Path

    import scitex_capture as _pkg

    return Path(_pkg.__file__).parent / "_skills" / "scitex-capture"


@skills_group.command("list")
@click.option("--json", "as_json", is_flag=True, default=False)
def _skills_list(as_json):
    """List bundled skill files.

    \b
    Example:
        $ scitex-capture skills list
        $ scitex-capture skills list --json
    """
    root = _skills_root()
    if not root.is_dir():
        if as_json:
            click.echo(json.dumps({"skills": []}))
        return
    skills = sorted(p.relative_to(root).as_posix() for p in root.rglob("*.md"))
    if as_json:
        click.echo(json.dumps({"skills": skills}, indent=2))
    else:
        for s in skills:
            click.echo(s)


@skills_group.command("get")
@click.argument("name")
@click.option("--json", "as_json", is_flag=True, default=False)
def _skills_get(name, as_json):
    """Print one bundled skill (relative path under _skills/scitex-capture/).

    \b
    Example:
        $ scitex-capture skills get SKILL.md
        $ scitex-capture skills get SKILL.md --json
    """
    p = _skills_root() / name
    if not p.is_file():
        click.echo(f"error: no such skill: {name}", err=True)
        sys.exit(1)
    body = p.read_text()
    if as_json:
        click.echo(json.dumps({"name": name, "content": body}, indent=2))
    else:
        click.echo(body)


@skills_group.command("install")
@click.option(
    "--dest",
    default="~/.claude/skills/scitex-capture",
    show_default=True,
    help="Where to copy the skills tree.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Print the actions that would be taken without copying anything.",
)
@click.option("-y", "--yes", is_flag=True, default=False, help="Assume yes (no-op).")
def _skills_install(dest, dry_run, yes):
    """Copy the bundled skills tree to ``dest`` (default: ~/.claude/skills/...).

    \b
    Example:
        $ scitex-capture skills install
        $ scitex-capture skills install --dest ~/my-skills
        $ scitex-capture skills install --dry-run
    """
    import shutil
    from pathlib import Path

    src = _skills_root()
    if not src.is_dir():
        click.echo("error: no _skills/scitex-capture/ to install", err=True)
        sys.exit(1)
    target = Path(dest).expanduser()
    if dry_run:
        click.echo(f"[dry-run] would install → {target}")
        for f in src.rglob("*.md"):
            click.echo(f"[dry-run]   {f.relative_to(src)}")
        return
    _ = yes  # accepted for §2 conformance; install is non-interactive
    target.mkdir(parents=True, exist_ok=True)
    for f in src.rglob("*.md"):
        rel = f.relative_to(src)
        out = target / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, out)
    click.echo(f"installed → {target}")


main.add_command(skills_group)

# §1a: install-shell-completion + print-shell-completion
try:
    from scitex_dev._cli._completion import attach_shell_completion

    attach_shell_completion(main, prog_name="scitex-capture")
except ImportError:
    pass

# §4: prepend canonical "<cli> (vX.Y.Z) — <description>" to root --help.
try:
    from importlib.metadata import version as _v

    main.help = (
        f"scitex-capture (v{_v('scitex-capture')}) — " + (main.help or "").lstrip()
    )
except Exception:
    pass


def cli_entrypoint():
    """Console-script entry — preprocess argv so ``scitex-capture
    <MESSAGE> --flag`` works, then hand off to Click."""
    sys.argv[1:] = _reorder_argv(sys.argv[1:])
    return main()


if __name__ == "__main__":
    sys.exit(cli_entrypoint() or 0)
