"""What the dashboard shows, computed without Streamlit so it can be tested."""


def summarise(rows: list[dict], by: str, value: str) -> list[dict]:
    """Total `value` per distinct `by`, in first-seen order."""
    totals: dict = {}
    for r in rows:
        totals[r[by]] = totals.get(r[by], 0) + r[value]
    return [{by: k, value: v} for k, v in totals.items()]
