import pytest
from datetime import datetime
from src.utils import (
    greetings,
    sort_by_date,
    get_card_info,
    get_top_transactions
)


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
    assert len(result) == 2  # 1 мая - 5 мая включительно


def test_sort_by_date_invalid():
    transactions = [{"Дата операции": "01.05.2024 10:00:00"}]
    result = sort_by_date(transactions, "invalid-date")
    assert result == []


def test_get_card_info():
    operations = [
        {"Номер карты": "*1234", "Сумма операции": -500.0, "Статус": "OK"},
        {"Номер карты": "*1234", "Сумма операции": -250.0, "Статус": "OK"},
        {"Номер карты": "*1234", "Сумма операции": 300.0, "Статус": "OK"},  # доход
        {"Номер карты": "*5678", "Сумма операции": -100.0, "Статус": "OK"},
        {"Номер карты": "*5678", "Сумма операции": -50.0, "Статус": "CANCELLED"},  # не OK
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
    assert result[0]["amount"] == 300.0  # наибольшая по модулю трата
    assert all("date" in item for item in result)
