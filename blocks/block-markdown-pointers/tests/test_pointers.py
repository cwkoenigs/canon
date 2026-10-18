import pytest

from {{package}}.pointers import pointer_problems, pointers

V = {"testing": 2}


@pytest.mark.parametrize("code", ["`[[x]]`", "``[[x]]``", "```\n[[x]]\n```\n", "~~~\n[[x]]\n~~~\n",
                                  "````md\n```\n[[x]]\n```\n````\n"])
def test_code_is_not_a_claim(code):
    assert pointer_problems(code + "\n[[nope]]\n", V) == ["[[nope]] is not in the canon"]


def test_pins():
    assert pointers("[[testing@1]] [[testing]]") == [("testing", 1), ("testing", None)]
    assert pointer_problems("[[testing@3]]", V) == ["[[testing@3]] pins a version the canon never had (current v2)"]


def test_unknown_id_is_reported_as_written():
    assert pointer_problems("[[nope@1]] and [[nope]]", V) == sorted(["[[nope@1]] is not in the canon", "[[nope]] is not in the canon"])
