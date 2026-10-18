import pytest

from {{package}}.schema import SchemaError, Variable, check_value, load_schema


def write_schema(tmp_path, text):
    path = tmp_path / "schema.toml"
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_loads_every_type(tmp_path):
    path = write_schema(
        tmp_path,
        """
[vars.A]
type = "string"

[vars.B]
type = "int"
required = true

[vars.C]
type = "bool"
default = "yes"

[vars.D]
type = "port"

[vars.E]
type = "url"

[vars.F]
type = "enum"
values = ["dev", "prod"]
""",
    )

    schema = load_schema(path)

    assert schema == {
        "A": Variable("string"),
        "B": Variable("int", required=True),
        "C": Variable("bool", default="yes"),
        "D": Variable("port"),
        "E": Variable("url"),
        "F": Variable("enum", values=("dev", "prod")),
    }


def test_empty_schema_is_allowed(tmp_path):
    assert load_schema(write_schema(tmp_path, "")) == {}


def test_missing_file_is_a_schema_error(tmp_path):
    with pytest.raises(SchemaError, match="cannot read"):
        load_schema(str(tmp_path / "missing.toml"))


def test_invalid_toml_is_a_schema_error(tmp_path):
    with pytest.raises(SchemaError, match="not valid TOML"):
        load_schema(write_schema(tmp_path, "[vars.A\n"))


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ('vars = 1\n', "vars must be a table"),
        ('other = 1\n', "unknown top-level key 'other'"),
        ('[vars.A]\nrequired = true\n', "vars.A.type must be one of"),
        ('[vars.A]\ntype = "float"\n', "vars.A.type must be one of"),
        ('[vars.A]\ntype = "int"\nrequied = true\n', "vars.A has unknown key 'requied'"),
        ('[vars.A]\ntype = "int"\nrequired = "yes"\n', "vars.A.required must be true or false"),
        ('[vars.A]\ntype = "int"\ndefault = 1\n', "vars.A.default must be a string"),
        ('[vars.A]\ntype = "int"\ndefault = "x"\n', "vars.A.default: expected an integer"),
        ('[vars.A]\ntype = "port"\ndefault = "0"\n', "vars.A.default: expected a port"),
        ('[vars.A]\ntype = "enum"\n', "vars.A.values must be a non-empty list of strings"),
        ('[vars.A]\ntype = "enum"\nvalues = []\n', "vars.A.values must be a non-empty list of strings"),
        ('[vars.A]\ntype = "enum"\nvalues = [1]\n', "vars.A.values must be a non-empty list of strings"),
        ('[vars.A]\ntype = "enum"\nvalues = ["x"]\ndefault = "y"\n', "vars.A.default: expected one of x"),
        ('[vars.A]\ntype = "string"\nvalues = ["x"]\n', "vars.A.values only applies to enum"),
        ('[vars.A]\ntype = "string"\n\n[vars]\nbad-name = 1\n', "invalid variable name 'bad-name'"),
        ("[vars]\nA = 1\n", "vars.A must be a table"),
    ],
)
def test_malformed_schema_is_a_schema_error(tmp_path, text, message):
    with pytest.raises(SchemaError, match=message):
        load_schema(write_schema(tmp_path, text))


@pytest.mark.parametrize(
    ("variable", "value", "fits"),
    [
        (Variable("string"), "", True),
        (Variable("string"), "anything at all", True),
        (Variable("int"), "0", True),
        (Variable("int"), "-12", True),
        (Variable("int"), "+7", True),
        (Variable("int"), "", False),
        (Variable("int"), "1.5", False),
        (Variable("int"), " 1", False),
        (Variable("int"), "1\n", False),
        (Variable("bool"), "TRUE", True),
        (Variable("bool"), "No", True),
        (Variable("bool"), "on", True),
        (Variable("bool"), "0", True),
        (Variable("bool"), "maybe", False),
        (Variable("port"), "1", True),
        (Variable("port"), "65535", True),
        (Variable("port"), "+80", True),
        (Variable("port"), "00080", True),
        (Variable("port"), "0", False),
        (Variable("port"), "65536", False),
        (Variable("port"), "-1", False),
        (Variable("port"), "999999999999999999999999", False),
        (Variable("port"), "http", False),
        (Variable("url"), "https://example.com", True),
        (Variable("url"), "postgres://user:pw@db:5432/app", True),
        (Variable("url"), "example.com", False),
        (Variable("url"), "https://", False),
        (Variable("url"), "http://[::1", False),
        (Variable("enum", values=("dev", "prod")), "prod", True),
        (Variable("enum", values=("dev", "prod")), "Prod", False),
        (Variable("enum", values=("dev", "prod")), "", False),
    ],
)
def test_check_value(variable, value, fits):
    assert (check_value(variable, value) is None) is fits
