"""Model: the second declared output. A baseline that predicts each entity's mean, so the pipeline
is end to end and testable before a real learner replaces this file."""


def train(features: list[dict], key: str, target: str = "mean") -> dict:
    return {"kind": "per-key-mean", "key": key, "table": {f[key]: f[target] for f in features}}


def predict(model: dict, keys: list) -> list[float]:
    table = model["table"]
    fallback = sum(table.values()) / len(table) if table else 0.0
    return [table.get(k, fallback) for k in keys]
