"""Smoke tests: every example script must run to completion."""

import subprocess
import sys
from pathlib import Path

import pytest

EXAMPLES = sorted(Path(__file__).parent.parent.parent.joinpath("examples").glob("*.py"))


def test_at_least_one_example_script_exists():
    # Arrange
    # Act
    found = EXAMPLES
    # Assert
    assert found, "no example scripts found"


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda p: p.name)
def test_example_script_runs_to_completion(example, tmp_path):
    # Arrange
    cmd = [sys.executable, str(example)]
    # Act
    result = subprocess.run(
        cmd,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Assert
    assert result.returncode == 0, f"{example.name} failed: {result.stderr}"
