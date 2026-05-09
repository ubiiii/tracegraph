from pathlib import Path

from tracegraph.utils.io import read_json, read_jsonl, read_pickle, read_yaml, write_json, write_jsonl, write_pickle, write_yaml


def test_json_roundtrip(tmp_path):
    p = tmp_path / "a.json"
    write_json(str(p), {"x": 1})
    assert read_json(str(p))["x"] == 1


def test_jsonl_roundtrip(tmp_path):
    p = tmp_path / "a.jsonl"
    rows = [{"a": 1}, {"b": 2}]
    write_jsonl(str(p), rows)
    assert read_jsonl(str(p)) == rows


def test_pickle_roundtrip(tmp_path):
    p = tmp_path / "a.pkl"
    write_pickle(str(p), {"x": [1, 2]})
    assert read_pickle(str(p))["x"] == [1, 2]


def test_yaml_roundtrip(tmp_path):
    p = tmp_path / "a.yaml"
    write_yaml(str(p), {"k": "v"})
    assert read_yaml(str(p))["k"] == "v"
