"""Unit Tests for `commands.py`."""

import pytest
import typer
from hypothesis import given
from hypothesis import strategies as st
from typer.testing import CliRunner

from ${{ carnate.project_name }} import commands

runner = CliRunner()


def test_what_am_i() -> None:
    """Test: Say hello to NAME."""
    assert commands.what_am_i("string") is None


def test_pword_nullity() -> None:
    """Test: Request input that needs to be hidden."""
    assert commands.pword("string") is None


def test_version_callback() -> None:
    """Test error and non-error exit."""
    assert commands.version_callback(False) is None
    with pytest.raises(typer.Exit):
        commands.version_callback(True)


@given(st.integers(min_value=0, max_value=20), st.integers(min_value=-10, max_value=10))
def test_numeric_intake(x: int, y: int) -> None:
    """Test numeric_intake with random inputs."""
    assert commands.numeric_intake(x, y) == x + y


# This will take innordinantely long with Hypothesis.
# @given(st.integers(min_value=1, max_value=36))
def test_spin_function() -> None:
    """Test acceptance of variable number of Spinners."""
    assert commands.spin(0) is None


def test_spin_command() -> None:
    """Test: that spin command returns a healthy exit code."""
    result = runner.invoke(commands.app, ["spin", "0"])
    assert result.exit_code == 0


# This will take innordinantely long with Hypothesis.
# @given(st.integers(min_value=1, max_value=16), st.booleans())
@given(st.booleans())
def test_progbar(
    plain_bar: bool,  # noqa: FBT001
) -> None:
    """Test inputs accepted for progress bars."""
    assert commands.progbar(0, plain_bar) is None

