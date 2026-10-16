import tomllib

import pytest
import yaml

from {{package}}.textsafe import check_one_line, check_project_name, fill_template, json_literal

HOSTILE = 'Print "hello" \\ 🚀 """ end\x7f'


def test_json_literal_is_valid_everywhere():
    lit = json_literal(HOSTILE)
    assert eval(lit) == HOSTILE
    assert tomllib.loads(f"x = {lit}")["x"] == HOSTILE
    assert yaml.safe_load(f"x: {lit}")["x"] == HOSTILE
    compile(f"{lit}\nx = 1\n", "m.py", "exec")            # as a module docstring


@pytest.mark.parametrize("bad", ["a\nb", "tab\there", "nul\x00", "sep "])
def test_one_line(bad):
    with pytest.raises(ValueError):
        check_one_line("purpose", bad)


@pytest.mark.parametrize("name", ["class", "match", "my--cli", "trailing-", "Caps", "x"])
def test_bad_names(name):
    with pytest.raises(ValueError):
        check_project_name(name)


def test_good_name():
    assert check_project_name("order-metrics") == "order_metrics"


def test_fill_is_one_pass():
    out = fill_template("{{a}} / {{b}} / {{missing}}", {"a": "{{b}}", "b": "B"})
    assert out == "{{b}} / B / {{missing}}"
