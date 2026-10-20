from {{package}}.report import build_report, write_report


def test_report_has_title_count_and_rows():
    text = build_report("Deaths by barn", [{"barn": "A", "deaths": 2}, {"barn": "B", "deaths": 0}])
    assert text.startswith("# Deaths by barn") and "2 rows." in text and "| A | 2 |" in text


def test_report_is_written_under_reports(tmp_path):
    path = write_report("# x\n", tmp_path / "reports")
    assert path.read_text() == "# x\n" and path.parent.name == "reports"
