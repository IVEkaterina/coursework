import json
import pandas as pd


from src.decorators import decorator_record_file

@decorator_record_file("test_output.json")
def test_func_returns_dataframe():
    return pd.DataFrame([{"name": "Alice", "age": 30}])

def test_decorator_saves_dataframe(tmp_path):
    file_path = tmp_path / "test_output.json"

    @decorator_record_file(file_path)
    def func():
        return pd.DataFrame([{"name": "Alice", "age": 30}])

    result = func()

    assert isinstance(result, pd.DataFrame)
    assert file_path.exists()

    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["name"] == "Alice"


def test_decorator_ignores_non_dataframe(tmp_path):
    file_path = tmp_path / "test_output.json"

    @decorator_record_file(file_path)
    def func():
        return {"not": "dataframe"}

    result = func()
    assert isinstance(result, dict)
    assert not file_path.exists()
