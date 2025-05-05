import pytest
from datetime import datetime

from proverka import spending_by_category


@pytest.fixture
def sample_transactions():
    # Подготовка фиктивных данных для тестов
    return [
        {"Дата операции": "22.03.2025 12:00:00", "Категория": "Другое", "Сумма платежа": -150, "Статус": "OK"},
        {"Дата операции": "23.03.2025 13:00:00", "Категория": "Другое", "Сумма платежа": -200, "Статус": "OK"},
        {"Дата операции": "24.03.2025 14:00:00", "Категория": "Другое", "Сумма платежа": -250, "Статус": "Failed"},
        {"Дата операции": "25.03.2025 15:00:00", "Категория": "Транспорт", "Сумма платежа": -100, "Статус": "OK"},
        {"Дата операции": "26.03.2025 16:00:00", "Категория": "Другое", "Сумма платежа": 100, "Статус": "OK"},
        {"Дата операции": "27.12.2024 17:00:00", "Категория": "Другое", "Сумма платежа": -300, "Статус": "OK"}
    ]


def test_spending_by_category_within_date_range(sample_transactions):
    # Тестируем фильтрацию по категории и дате
    result = spending_by_category(sample_transactions, "Другое", "27.04.2025")

    # Проверяем, что в результате только те транзакции, которые соответствуют категории и дате
    assert len(result) == 2
    assert all(item["Категория"] == "Другое" for item in result)
    assert all(item["Сумма платежа"] < 0 for item in result)
    assert all(item["Статус"] == "OK" for item in result)


def test_spending_by_category_with_no_date(sample_transactions):
    # Тестируем работу без передачи даты (в этом случае берется текущая дата)
    result = spending_by_category(sample_transactions, "Другое")

    # Проверяем, что результат не пустой
    assert len(result) > 0


def test_spending_by_category_with_invalid_category(sample_transactions):
    # Тестируем случай, когда нет транзакций для указанной категории
    result = spending_by_category(sample_transactions, "Еда", "23.12.2021")

    # Проверяем, что результат пуст
    assert len(result) == 0


def test_spending_by_category_with_no_valid_transactions(sample_transactions):
    # Тестируем случай, когда нет транзакций, которые соответствуют всем фильтрам
    result = spending_by_category(sample_transactions, "Другое", "26.12.2021")

    # Проверяем, что результат пуст
    assert len(result) == 0


def test_spending_by_category_with_mixed_status(sample_transactions):
    # Тестируем фильтрацию по статусу "OK" (только транзакции с этим статусом должны быть возвращены)
    result = spending_by_category(sample_transactions, "Другое", "23.12.2021")

    # Проверяем, что в результате только те транзакции, которые имеют статус "OK"
    assert all(item["Статус"] == "OK" for item in result)


def test_spending_by_category_total_spent(sample_transactions):
    # Проверяем правильность подсчета суммы
    result = spending_by_category(sample_transactions, "Другое", "23.04.2025")
    total_spent = sum(abs(item["Сумма платежа"]) for item in result)

    # Проверка, что сумма расходов правильно подсчитана
    assert total_spent == 350  # (-150) + (-200) = 350
