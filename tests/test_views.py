import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.views import main_func_for_views  # Предполагаем, что функция находится в src/views.py


# Тест: корректный формат даты и времени
@patch("src.views.read_transactions_from_excel")
@patch("src.views.load_user_settings")
@patch("src.views.sort_by_date")
@patch("src.views.greetings")
@patch("src.views.get_card_info")
@patch("src.views.get_top_transactions")
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
def test_main_func_for_views(mock_get_stock_prices, mock_get_currency_rates, mock_get_top_transactions,
                             mock_get_card_info, mock_greetings, mock_sort_by_date, mock_load_user_settings,
                             mock_read_transactions_from_excel):
    # Мокаем возвращаемые значения
    mock_read_transactions_from_excel.return_value = [
        {"date": "2023-05-02", "amount": 100, "category": "Food", "description": "Groceries"},
        {"date": "2023-05-03", "amount": 50, "category": "Transport", "description": "Taxi"}
    ]
    mock_load_user_settings.return_value = {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "GOOGL"]
    }
    mock_sort_by_date.return_value = [
        {"date": "2023-05-02", "amount": 100, "category": "Food", "description": "Groceries"}]
    mock_greetings.return_value = "Good afternoon!"
    mock_get_card_info.return_value = [{
        "last_digits": "1234",
        "total_spent": 1000,
        "cashback": 10
    }]
    mock_get_top_transactions.return_value = [
        {"date": "2023-05-02", "amount": 100, "category": "Food", "description": "Groceries"}]
    mock_get_currency_rates.return_value = [{"currency": "USD", "rate": 75.0}, {"currency": "EUR", "rate": 90.0}]
    mock_get_stock_prices.return_value = [{"stock": "AAPL", "price": 150.0}, {"stock": "GOOGL", "price": 2800.0}]

    # Дата и время в правильном формате
    datetime_str = "2023-05-02 15:30:00"

    # Вызов функции
    result = main_func_for_views(datetime_str)

    # Проверки
    assert result["greeting"] == "Good afternoon!"
    assert len(result["cards"]) == 1
    assert result["cards"][0]["last_digits"] == "1234"
    assert result["top_transactions"][0]["category"] == "Food"
    assert result["currency_rates"][0]["currency"] == "USD"
    assert result["stock_prices"][0]["stock"] == "AAPL"


# Тест: некорректный формат даты
@patch("src.views.read_transactions_from_excel")
@patch("src.views.load_user_settings")
@patch("src.views.sort_by_date")
@patch("src.views.greetings")
@patch("src.views.get_card_info")
@patch("src.views.get_top_transactions")
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
def test_main_func_for_views_invalid_date(mock_get_stock_prices, mock_get_currency_rates, mock_get_top_transactions,
                                          mock_get_card_info, mock_greetings, mock_sort_by_date,
                                          mock_load_user_settings, mock_read_transactions_from_excel):
    # Мокаем возвращаемые значения
    mock_read_transactions_from_excel.return_value = []
    mock_load_user_settings.return_value = {}

    # Некорректная дата
    datetime_str = "2023-05-02 15:30"  # Отсутствует секунды

    # Вызов функции
    result = main_func_for_views(datetime_str)

    # Проверки
    assert result == {}  # Возвращаем пустой словарь в случае ошибки
