import re
from pathlib import Path

ASSIGNMENT = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=(.*)")
TRAILING_COMMENT = re.compile(r"(^|\s)#.*$")
DOUBLE_QUOTE_ESCAPES = {"n": "\n", "t": "\t", "\\": "\\", '"': '"', "$": "$"}


class ParseError(ValueError):
    """A line that is not a valid dotenv assignment."""


def parse_line(line: str) -> tuple[str, str] | None:
    """Return (name, value) for an assignment, or None for a blank or comment line."""
    text = line.strip()
    if not text or text.startswith("#"):
        return None
    text = re.sub(r"^export\s+", "", text)
    match = ASSIGNMENT.fullmatch(text)
    if match is None:
        raise ParseError("expected NAME=value")
    return match.group(1), _parse_value(match.group(2).lstrip())


def read_env(filename: str) -> tuple[dict[str, str], list[str]]:
    """Read a dotenv file. Returns its variables and one error line per unparseable line."""
    values: dict[str, str] = {}
    errors: list[str] = []
    text = Path(filename).read_text(encoding="utf-8-sig")
    for number, line in enumerate(text.split("\n"), start=1):
        try:
            assignment = parse_line(line)
        except ParseError as exc:
            errors.append(f"ERROR {filename}:{number}: {exc}")
            continue
        if assignment is not None:
            name, value = assignment
            values[name] = value
    return values, errors


def _parse_value(raw: str) -> str:
    if raw.startswith("'"):
        end = raw.find("'", 1)
        if end == -1:
            raise ParseError("unterminated single-quoted value")
        return _end_quoted(raw[1:end], raw[end + 1 :])
    if raw.startswith('"'):
        value, tail = _parse_double_quoted(raw)
        return _end_quoted(value, tail)
    return TRAILING_COMMENT.sub("", raw).strip()


def _parse_double_quoted(raw: str) -> tuple[str, str]:
    chars = []
    index = 1
    while index < len(raw):
        char = raw[index]
        if char == '"':
            return "".join(chars), raw[index + 1 :]
        if char == "\\":
            index += 1
            escape = raw[index : index + 1]
            if escape not in DOUBLE_QUOTE_ESCAPES:
                raise ParseError(f"unknown escape '\\{escape}' in double-quoted value")
            char = DOUBLE_QUOTE_ESCAPES[escape]
        chars.append(char)
        index += 1
    raise ParseError("unterminated double-quoted value")


def _end_quoted(value: str, tail: str) -> str:
    rest = tail.strip()
    if rest and not rest.startswith("#"):
        raise ParseError("unexpected text after closing quote")
    return value
