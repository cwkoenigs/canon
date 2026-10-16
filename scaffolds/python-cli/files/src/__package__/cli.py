import typer

from . import __version__

app = typer.Typer(help={{purpose_json}}, no_args_is_help=True)


@app.command()
def version() -> None:
    """Print the version."""
    typer.echo(__version__)


@app.command()
def hello(name: str = "world") -> None:
    """Say hello. Replace with the first real command."""
    typer.echo(f"hello, {name}")
