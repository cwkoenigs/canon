import re
import tomllib
from dataclasses import dataclass
from urllib.parse import urlsplit

NAME_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
INT_PATTERN = re.compile(r"[+-]?[0-9]+")
TYPES = ("string", "int", "bool", "port", "url", "enum")
BOOL_WORDS = frozenset({"true", "false", "yes", "no", "on", "off", "1", "0"})
VARIABLE_KEYS = frozenset({"type", "required", "default", "values"})


class SchemaError(Exception):
    """The schema file cannot be read or is malformed."""


@dataclass(frozen=True)
class Variable:
    type: str
    required: bool = False
    default: str | None = None
    values: tuple[str, ...] = ()


def load_schema(path: str) -> dict[str, Variable]:
    try:
        with open(path, "rb") as file:
            data = tomllib.load(file)
    except OSError as exc:
        raise SchemaError(f"cannot read {path}: {exc.strerror or exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise SchemaError(f"{path} is not valid TOML: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise SchemaError(f"{path} is not valid UTF-8") from exc
    return _parse_schema(data)


def check_value(variable: Variable, value: str) -> str | None:
    """Return what is wrong with value for its type, or None if it fits."""
    kind = variable.type
    if kind == "int" and not INT_PATTERN.fullmatch(value):
        return f"expected an integer, got {value!r}"
    if kind == "bool" and value.lower() not in BOOL_WORDS:
        return f"expected a boolean, got {value!r}"
    if kind == "port" and not _is_port(value):
        return f"expected a port (1-65535), got {value!r}"
    if kind == "url" and not _is_url(value):
        return f"expected a URL with a scheme and host, got {value!r}"
    if kind == "enum" and value not in variable.values:
        return f"expected one of {', '.join(variable.values)}, got {value!r}"
    return None


def _parse_schema(data: dict) -> dict[str, Variable]:
    unknown = sorted(set(data) - {"vars"})
    if unknown:
        raise SchemaError(f"unknown top-level key {unknown[0]!r}")
    tables = data.get("vars", {})
    if not isinstance(tables, dict):
        raise SchemaError("vars must be a table")
    return dict(_parse_variable(name, spec) for name, spec in tables.items())


def _parse_variable(name: str, spec: object) -> tuple[str, Variable]:
    where = f"vars.{name}"
    if not NAME_PATTERN.fullmatch(name):
        raise SchemaError(f"invalid variable name {name!r}")
    if not isinstance(spec, dict):
        raise SchemaError(f"{where} must be a table")
    unknown = sorted(set(spec) - VARIABLE_KEYS)
    if unknown:
        raise SchemaError(f"{where} has unknown key {unknown[0]!r}")
    kind = spec.get("type")
    if kind not in TYPES:
        raise SchemaError(f"{where}.type must be one of {', '.join(TYPES)}")
    required = spec.get("required", False)
    if not isinstance(required, bool):
        raise SchemaError(f"{where}.required must be true or false")
    default = spec.get("default")
    if default is not None and not isinstance(default, str):
        raise SchemaError(f"{where}.default must be a string")
    values: tuple[str, ...] = ()
    if kind == "enum":
        listed = spec.get("values")
        if not isinstance(listed, list) or not listed or not all(isinstance(v, str) for v in listed):
            raise SchemaError(f"{where}.values must be a non-empty list of strings")
        values = tuple(listed)
    elif "values" in spec:
        raise SchemaError(f"{where}.values only applies to enum")
    variable = Variable(kind, required, default, values)
    if default is not None:
        problem = check_value(variable, default)
        if problem:
            raise SchemaError(f"{where}.default: {problem}")
    return name, variable


def _is_port(value: str) -> bool:
    if not INT_PATTERN.fullmatch(value) or value.startswith("-"):
        return False
    digits = value.lstrip("+0")
    return len(digits) <= 5 and 1 <= int(digits or "0") <= 65535


def _is_url(value: str) -> bool:
    try:
        parts = urlsplit(value)
        return bool(parts.scheme) and bool(parts.hostname)
    except ValueError:
        return False
