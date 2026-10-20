from {{package}}.features import build_features
from {{package}}.train import predict, train

ROWS = [{"barn": "A", "deaths": 2}, {"barn": "A", "deaths": 4}, {"barn": "B", "deaths": 1}]


def test_features_per_key():
    f = build_features(ROWS, key="barn", value="deaths")
    assert f == [{"barn": "A", "count": 2, "total": 6.0, "mean": 3.0},
                 {"barn": "B", "count": 1, "total": 1.0, "mean": 1.0}]


def test_model_predicts_known_and_unknown_keys():
    m = train(build_features(ROWS, key="barn", value="deaths"), key="barn")
    assert predict(m, ["A", "B", "C"]) == [3.0, 1.0, 2.0]
