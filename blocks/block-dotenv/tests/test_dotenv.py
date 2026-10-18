import pytest

from {{package}}.dotenv import ParseError, parse_line


@pytest.mark.parametrize("line", ["", "   ", "# a comment", "   # indented comment"])
def test_blank_and_comment_lines_are_skipped(line):
    assert parse_line(line) is None


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("NAME=value", ("NAME", "value")),
        ("NAME=", ("NAME", "")),
        ("NAME=  value  # note", ("NAME", "value")),
        ("NAME=b#c", ("NAME", "b#c")),
        ("NAME=# only a comment", ("NAME", "")),
        ("export NAME=1", ("NAME", "1")),
        ("export   NAME=1", ("NAME", "1")),
        ("_name9=x", ("_name9", "x")),
        ("NAME='x # y\\n'", ("NAME", "x # y\\n")),
        ("NAME=' spaced '", ("NAME", " spaced ")),
        ("NAME='x' # ok", ("NAME", "x")),
        ('NAME="a\\tb\\n\\\\\\"\\$"', ("NAME", "a\tb\n\\\"$")),
        ('NAME="x # y"', ("NAME", "x # y")),
        ('NAME=""', ("NAME", "")),
    ],
)
def test_values(line, expected):
    assert parse_line(line) == expected


@pytest.mark.parametrize(
    "line",
    [
        "NAME",
        "1NAME=x",
        "NAME-X=x",
        "NAME = x",
        "export",
        "NAME='x",
        'NAME="x',
        'NAME="x\\q"',
        "NAME='x'junk",
        'NAME="x" junk',
    ],
)
def test_unparseable_lines_raise(line):
    with pytest.raises(ParseError):
        parse_line(line)
