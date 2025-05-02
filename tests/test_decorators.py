import pandas as pd
from src.decorators import decorator_record_file
from unittest.mock import patch
import pytest

# 1. Тест: функция возвращает DataFrame => должен быть вызов to_json
@patch("pandas.DataFrame.to_json")
def test_decorator_writes_json(mock_to_json):
    @decorator_record_file("fake_file.json")
    def dummy_func():
        return pd.DataFrame({"col": [1, 2, 3]})

    result = dummy_func()

    assert isinstance(result, pd.DataFrame)
    mock_to_json.assert_called_once_with("fake_file.json", orient="records", lines=True, force_ascii=False)

# 2. Тест: функция возвращает НЕ DataFrame => to_json не вызывается
@patch("pandas.DataFrame.to_json")
def test_decorator_does_not_write_on_invalid_data(mock_to_json, caplog):
    @decorator_record_file("should_not_write.json")
    def dummy_func():
        return "not a dataframe"

    with caplog.at_level("ERROR"):
        result = dummy_func()

    assert result == "not a dataframe"
    mock_to_json.assert_not_called()
    assert "Данные не являются датафреймом" in caplog.text

# 3. Тест: реально создаётся файл с содержимым (не mock, а tmp_path)
def test_decorator_creates_real_file(tmp_path):
    output_file = tmp_path / "output.json"

    @decorator_record_file(output_file)
    def dummy_func():
        return pd.DataFrame({"name": ["Alice"], "age": [30]})

    dummy_func()

    assert output_file.exists()
    with open(output_file, encoding="utf-8") as f:
        content = f.read()
        assert "Alice" in content
