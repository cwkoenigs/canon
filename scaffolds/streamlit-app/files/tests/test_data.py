from {{package}}.data import summarise


def test_summarise_totals_in_first_seen_order():
    rows = [{"barn": "A", "deaths": 2}, {"barn": "B", "deaths": 1}, {"barn": "A", "deaths": 1}]
    assert summarise(rows, by="barn", value="deaths") == [{"barn": "A", "deaths": 3}, {"barn": "B", "deaths": 1}]
