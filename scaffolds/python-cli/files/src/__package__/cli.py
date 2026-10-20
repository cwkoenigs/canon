"""The command-line entry point. Output goes through the team's terminal design system
([[terminal-design]]): outcome lines, labelled rows, errors that say the fix."""
import sys

import typer
from canon_lib.ui_style import console, outcome

from . import __version__

app = typer.Typer(help={{purpose_json}}, no_args_is_help=True)
out = console(color=sys.stdout.isatty())      # colour on a terminal, plain glyphs in a log


@app.command()
def version() -> None:
    """Print the version."""
    typer.echo(__version__)


@app.command()
def hello(name: str = "world") -> None:
    """Say hello. Replace with the first real command."""
    out.print(outcome("ok", "hello", name))
