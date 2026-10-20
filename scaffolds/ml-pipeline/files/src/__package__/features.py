"""Features: the first declared output. Source rows in, one feature row per entity out."""


def build_features(rows: list[dict], key: str, value: str) -> list[dict]:
    """Per `key`: count, total and mean of `value`. Deterministic, no I/O."""
    acc: dict = {}
    for r in rows:
        c, t = acc.get(r[key], (0, 0.0))
        acc[r[key]] = (c + 1, t + float(r[value]))
    return [{key: k, "count": c, "total": t, "mean": t / c} for k, (c, t) in acc.items()]
