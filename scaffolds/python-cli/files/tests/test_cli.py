from typer.testing import CliRunner

from {{package}}.cli import app


def test_version():
    result = CliRunner().invoke(app, ["version"])
    assert result.exit_code == 0 and result.stdout.strip() == "0.1.0"
