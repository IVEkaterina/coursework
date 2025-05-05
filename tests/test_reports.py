import pandas as pd

from src.reports import spending_by_category

TEST_TRANSACTIONS = pd.DataFrame([
    {
        "Дата операции": "01.04.2024 12:00:00",
        "Категория": "Еда",
        "Сумма платежа": -500.0,
        "Статус": "OK"
    },
    {
        "Дата операции": "15.02.2024 08:30:00",
        "Категория": "Еда",
        "Сумма платежа": -1000.0,
        "Статус": "OK"
    },
    {
        "Дата операции": "01.01.2024 12:00:00",
        "Категория": "Еда",
        "Сумма платежа": -200.0,
        "Статус": "OK"
    },
    {
        "Дата операции": "20.03.2024 15:00:00",
        "Категория": "Транспорт",
        "Сумма платежа": -300.0,
        "Статус": "OK"
    },
    {
        "Дата операции": "01.04.2024 12:00:00",
        "Категория": "Еда",
        "Сумма платежа": -500.0,
        "Статус": "FAILED"
    },
])

def test_spending_by_category_with_date():
    """
    Проверка выборки по дате и категории: берём только последние 3 месяца от 01.04.2024
    """
    result = spending_by_category(TEST_TRANSACTIONS, category="Еда", date="01.04.2024")
    assert not result.empty
    assert len(result) == 2
    assert pd.Series(result["Категория"] == "Еда").all()
    assert pd.Series(result["Статус"] == "OK").all()
    assert pd.Series(result["Сумма платежа"] < 0).all()


def test_spending_by_category_without_date():
    """
    Проверка без передачи даты (используется текущая дата)
    """
    result = spending_by_category(TEST_TRANSACTIONS, category="Транспорт")
    assert isinstance(result, pd.DataFrame)


def test_spending_by_category_no_matches():
    """
    Проверка: нет совпадений по категории
    """
    result = spending_by_category(TEST_TRANSACTIONS, category="Подарки", date="01.04.2024")
    assert result.empty


def test_spending_by_category_invalid_date_format():
    """
    Проверка на неверный формат даты — должна поймать исключение и вернуть пустой DataFrame
    """
    result = spending_by_category(TEST_TRANSACTIONS, category="Еда", date="2024/04/01")
    assert isinstance(result, pd.DataFrame)
    assert result.empty
