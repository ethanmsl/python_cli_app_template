"""*De facto* `main`.

Holding the key functions acting as entry points
to any other code and acting as the bridge to the user via
the typer framework and decorators.
"""

from __future__ import annotations

import time
from importlib import metadata
from typing import Optional

import typer
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn, track
from rich.prompt import Prompt

from . import __name__

# ^ uses parent's `__name__` to dynamically get the name of the app
# note: this may be separate from the name used to call the app via cli
# (e.g. `ripgrep` is an app, but it is called with `rg`)

# generate CLI app object
app = typer.Typer(rich_markup_mode="rich", add_completion=False)

##################################################################################
# Version Call Boilerplate
##################################################################################

# get version from pyproject.toml
__version__ = metadata.version(__package__)


def version_callback(version: bool) -> None:
    """Print app version and exit."""
    if version:
        rprint(f"{__name__} ('${{ carnate.cli_app_name }}') Version: {__version__}")
        raise typer.Exit(code=0)


@app.callback(help="[bold]${{ carnate.project_name }}[/bold] CLI App for [green]PagerDuty[/green]")
def app_options(
    _: bool = typer.Option(
        None,
        "--version",
        help="Show version of this app",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Make a callback to get version.

    **Base App** calls Callback.
    Sub-callbacks are used by the options to perform actions.
    The eager sub-callback allows us to circumvent typer's expectation that a regular
    command is still comming.

    (Side Note: Yes, I agree this is slightly awkward for something as standard as
    `--version`, but it does seem to be the best way to do it in this framework.)
    """


##################################################################################
# Regular 'ol Commands
##################################################################################


@app.command(rich_help_panel="Prompted")
def what_am_i(name: Optional[str] = typer.Argument(None)) -> None:
    """Share your name -- get a fun fact."""
    if name is None:
        name_out: str = Prompt.ask("Enter your name, plz :sunglasses:")
    else:
        name_out: str = name

    rprint(f"\nWhat, {name_out}, are you?")
    # example of using rich-print's MarkUp
    rprint(
        f"[green]Why you are [bold red]loved[/bold red][/green] \
[blue]{name_out}[/blue][green]![/green] :heart:"
    )


@app.command(rich_help_panel="Prompted")
def pword(
    name: str = "user",
    _: str = typer.Option(
        ...,
        "--hidden-input-string",
        prompt=True,
        confirmation_prompt=True,
        hide_input=True,
    ),
    # NOTE: we would NOT want this as it allows explicit flag calling and regular
    #       code inputing
) -> None:
    """Request input that needs to be hidden."""
    rprint(
        f"Hello [blue]{name}[/blue]. Doing something very secure :lock: with password."
    )


@app.command(rich_help_panel="Prompted")
def adding_tags() -> None:
    """Use Rich's prompt to add tags to a ticket."""
    tags = []
    while True:
        tag = Prompt.ask("Enter a tag, or [bold red]q[/bold red] to quit")
        if tag == "q":
            break
        tags.append(tag)
    rprint(f"Tags: {tags}")


##################################################################################
# Visual Widgets
##################################################################################


@app.command(rich_help_panel="Visual")
def spin(seconds: int = typer.Argument(5, min=0, max=36)) -> None:
    """Generate Spinners.

    For the unknowably long and asynchronous.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}", justify="right"),
        transient=True,
    ) as progress:
        progress.add_task("Task A...", total=seconds)
        task = progress.add_task("Task B...", total=seconds)
        for _ in range(seconds):
            time.sleep(1)
            progress.advance(task)


@app.command(rich_help_panel="Visual")
def progbar(
    seconds: int = typer.Argument(5, min=0, max=16),
    plain_bar: bool = False,
) -> None:
    """Generate progress bar in terminal."""
    if not plain_bar:
        total_so_far: int = 0
        for _ in track(range(seconds), description="Sleeping..."):
            time.sleep(1)
            total_so_far += 1
        rprint(f"Done sleeping for {total_so_far} seconds")
    else:
        total_so_far_2 = 0
        with typer.progressbar(range(seconds), label="Sleeping...") as progress:
            for _ in progress:
                time.sleep(1)
                total_so_far_2 += 1
        rprint(f"Done sleeping for {total_so_far_2} seconds")


##################################################################################
# Additional Validations
##################################################################################


@app.command(rich_help_panel="Additional Validations")
def numeric_intake(
    x_int: int = typer.Argument(..., min=0, max=20),
    y_int: int = typer.Argument(..., min=-10, max=10),
) -> int:
    """Take in `min` and `max`, with restrictions."""
    rprint(f"[blue]X[/blue]: {x_int}, [green]Y[/green]: {y_int}")
    return x_int + y_int
