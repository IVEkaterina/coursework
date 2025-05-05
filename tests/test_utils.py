import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.utils import (
    get_card_info,
    get_currency_rates,
    get_stock_prices,
    get_top_transactions,
    greetings,
    load_user_settings,
    read_transactions_from_excel,
    sort_by_date,
)


def test_read_transactions_success(tmp_path):
    df = pd.DataFrame([
        {"amount": 100, "category": "Food"},
        {"amount": 200, "category": "Transport"},
    ])

    test_file = tmp_path / "test.xlsx"
    df.to_excel(test_file, index=False)

    result = read_transactions_from_excel(str(test_file))

    assert isinstance(result, list)
    assert result == [
        {"amount": 100, "category": "Food"},
        {"amount": 200, "category": "Transport"}
    ]


def test_read_transactions_file_not_found():
    result = read_transactions_from_excel("non_existing_file.xlsx")
    assert result == []


def test_read_transactions_invalid_file(tmp_path):
    bad_file = tmp_path / "not_excel.txt"
    bad_file.write_text("Это не Excel")

    result = read_transactions_from_excel(str(bad_file))
    assert result == []


def test_load_user_settings(tmp_path):
    test_data = {"theme": "dark", "language": "ru"}

    test_file = tmp_path / "user_settings.json"
    test_file.write_text(json.dumps(test_data, ensure_ascii=False), encoding='utf-8')

    result = load_user_settings(str(test_file))

    assert isinstance(result, dict)
    assert result == test_data


def test_load_user_settings_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_user_settings("non_existing_file.json")


@patch("src.utils.requests.get")
@patch("src.utils.os.getenv", return_value="fake_api_key")
def test_get_currency_rates_success(mock_getenv, mock_requests_get):
    """Тест успешного получения курса"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": {
            "RUB": {"value": 1},
            "USD": {"value": 0.01},
            "EUR": {"value": 0.012}
        }
    }
    mock_requests_get.return_value = mock_response

    result = get_currency_rates(["USD", "EUR"])

    assert result == [
        {"currency": "USD", "rate": 100.0},
        {"currency": "EUR", "rate": 83.33}
    ]


@patch("src.utils.os.getenv", return_value=None)
def test_get_currency_rates_no_api_key(mock_getenv):
    """отсутствует API-ключ"""
    result = get_currency_rates(["USD"])
    assert result == []


@patch("src.utils.requests.get")
@patch("src.utils.os.getenv", return_value="fake_api_key")
def test_get_currency_rates_no_rub(mock_getenv, mock_requests_get):
    """RUB отсутствует в ответе API"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": {
            "USD": {"value": 0.01}
        }
    }
    mock_requests_get.return_value = mock_response

    result = get_currency_rates(["USD"])
    assert result == []


@patch("src.utils.requests.get")
@patch("src.utils.os.getenv", return_value="fake_api_key")
def test_get_currency_rates_zero_value(mock_getenv, mock_requests_get):
    """курс валюты равен 0"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": {
            "RUB": {"value": 1},
            "USD": {"value": 0}
        }
    }
    mock_requests_get.return_value = mock_response

    result = get_currency_rates(["USD"])
    assert result == []


@patch("src.utils.requests.get")
@patch("src.utils.os.getenv", return_value="fake_api_key")
def test_get_currency_rates_missing_currency(mock_getenv, mock_requests_get):
    """валюта отсутствует в ответе API"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": {
            "RUB": {"value": 1}
        }
    }
    mock_requests_get.return_value = mock_response

    result = get_currency_rates(["USD"])
    assert result == []


@patch("src.utils.requests.get", side_effect=Exception("Ошибка соединения"))
@patch("src.utils.os.getenv", return_value="fake_api_key")
def test_get_currency_rates_exception(mock_getenv, mock_requests_get):
    """Происходит исключение"""
    result = get_currency_rates(["USD"])
    assert result == []


@patch("src.utils.requests.get")
@patch("src.utils.os.getenv", return_value="fake_stock_key")
def test_get_stock_prices_success(mock_getenv, mock_requests_get):
    """Успешный запрос с двумя акциями"""
    mock_response = MagicMock()
    mock_response.json.return_value = {"c": 145.75}
    mock_requests_get.return_value = mock_response

    result = get_stock_prices(["AAPL", "MSFT"])

    assert result == [
        {"stock": "AAPL", "price": 145.75},
        {"stock": "MSFT", "price": 145.75}
    ]


@patch("src.utils.os.getenv", return_value=None)
def test_get_stock_prices_no_api_key(mock_getenv):
    """Нет API-ключа"""
    result = get_stock_prices(["AAPL"])
    assert result == []


@patch("src.utils.requests.get")
@patch("src.utils.os.getenv", return_value="fake_stock_key")
def test_get_stock_prices_missing_price(mock_getenv, mock_requests_get):
    """Отсутствует цена ("c" нет в ответе API)"""
    mock_response = MagicMock()
    mock_response.json.return_value = {}  # нет "c"
    mock_requests_get.return_value = mock_response

    result = get_stock_prices(["AAPL"])
    assert result == []  # пусто, так как цена не найдена


@patch("src.utils.requests.get")
@patch("src.utils.os.getenv", return_value="fake_stock_key")
def test_get_stock_prices_zero_price(mock_getenv, mock_requests_get):
    """Цена равна 0 (по логике функции — считается ценой и включается)"""
    mock_response = MagicMock()
    mock_response.json.return_value = {"c": 0}
    mock_requests_get.return_value = mock_response

    result = get_stock_prices(["AAPL"])
    assert result == []


@pytest.mark.parametrize("input_time,expected_greeting", [
    ("01:30:00", "Доброй ночи!"),
    ("06:00:00", "Доброе утро!"),
    ("13:00:00", "Добрый день!"),
    ("18:00:00", "Добрый вечер!"),
])
def test_greetings(input_time, expected_greeting):
    assert greetings(input_time) == expected_greeting


def test_greetings_invalid_time():
    with pytest.raises(ValueError):
        greetings("invalid-time")


def test_sort_by_date_valid():
    input_date = "05.05.2024"
    transactions = [
        {"Дата операции": "01.05.2024 10:00:00"},
        {"Дата операции": "03.05.2024 12:00:00"},
        {"Дата операции": "06.05.2024 15:00:00"},
    ]
    result = sort_by_date(transactions, input_date)
    assert len(result) == 2


def test_sort_by_date_invalid():
    transactions = [{"Дата операции": "01.05.2024 10:00:00"}]
    result = sort_by_date(transactions, "invalid-date")
    assert result == []


def test_get_card_info():
    operations = [
        {"Номер карты": "*1234", "Сумма операции": -500.0, "Статус": "OK"},
        {"Номер карты": "*1234", "Сумма операции": -250.0, "Статус": "OK"},
        {"Номер карты": "*1234", "Сумма операции": 300.0, "Статус": "OK"},
        {"Номер карты": "*5678", "Сумма операции": -100.0, "Статус": "OK"},
        {"Номер карты": "*5678", "Сумма операции": -50.0, "Статус": "CANCELLED"},
    ]
    result = get_card_info(operations)
    assert len(result) == 2
    assert any(card["last_digits"] == "1234" and card["total_spent"] == 750.0 for card in result)
    assert any(card["last_digits"] == "5678" and card["total_spent"] == 100.0 for card in result)


def test_get_top_transactions():
    operations = [
        {"Сумма операции": -100.0, "Дата операции": "01.05.2024 10:00:00",
         "Категория": "Еда", "Описание": "Обед"},
        {"Сумма операции": -250.0, "Дата операции": "02.05.2024 12:00:00",
         "Категория": "Одежда", "Описание": "Куртка"},
        {"Сумма операции": -300.0, "Дата операции": "03.05.2024 15:00:00",
         "Категория": "Техника", "Описание": "Наушники"},
        {"Сумма операции": -50.0, "Дата операции": "04.05.2024 18:00:00",
         "Категория": "Кофе", "Описание": "Капучино"},
        {"Сумма операции": -200.0, "Дата операции": "05.05.2024 20:00:00",
         "Категория": "Транспорт", "Описание": "Такси"},
        {"Сумма операции": 1000.0, "Дата операции": "06.05.2024 09:00:00",
         "Категория": "Зарплата", "Описание": "Доход"},
    ]
    result = get_top_transactions(operations)
    assert len(result) == 5
    assert result[0]["amount"] == 300.0
    assert all("date" in item for item in result)
