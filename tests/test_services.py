from unittest.mock import patch

from src.services import get_sort_bank_operations


def test_get_sort_bank_operations_match():
    """Операции, соответствующие строке поиска"""
    operations = [
        {"Описание": "Оплата счета", "Категория": "ЖКХ"},
        {"Описание": "Перевод на карту", "Категория": "Трансакции"},
        {"Описание": "Покупка в магазине", "Категория": "Товары"}
    ]
    search_string = "счет"

    result = get_sort_bank_operations(operations, search_string)

    assert len(result) == 1
    assert result[0]["Описание"] == "Оплата счета"
    assert result[0]["Категория"] == "ЖКХ"


def test_get_sort_bank_operations_no_match():
    """Нет совпадений для строки поиска"""
    operations = [
        {"Описание": "Оплата счета", "Категория": "ЖКХ"},
        {"Описание": "Перевод на карту", "Категория": "Трансакции"},
        {"Описание": "Покупка в магазине", "Категория": "Товары"}
    ]
    search_string = "кредит"

    result = get_sort_bank_operations(operations, search_string)

    assert len(result) == 0


def test_get_sort_bank_operations_case_insensitive():
    """Строки поиска не чувствительны к регистру"""
    operations = [
        {"Описание": "Оплата счета", "Категория": "ЖКХ"},
        {"Описание": "Перевод на карту", "Категория": "Трансакции"},
        {"Описание": "Покупка в магазине", "Категория": "Товары"}
    ]
    search_string = "ОПЛАТА"

    result = get_sort_bank_operations(operations, search_string)

    assert len(result) == 1
    assert result[0]["Описание"] == "Оплата счета"


def test_get_sort_bank_operations_empty_description_or_category():
    """Операции без описания или категории"""
    operations = [
        {"Описание": "", "Категория": "ЖКХ"},
        {"Описание": "Перевод на карту", "Категория": ""},
        {"Описание": "Покупка в магазине", "Категория": "Товары"}
    ]
    search_string = "Перевод"

    result = get_sort_bank_operations(operations, search_string)

    assert len(result) == 1
    assert result[0]["Описание"] == "Перевод на карту"


def test_get_sort_bank_operations_empty_operations():
    """Пустой список операций"""
    operations = []
    search_string = "оплата"

    result = get_sort_bank_operations(operations, search_string)

    assert len(result) == 0


def test_get_sort_bank_operations_warning_when_no_match():
    """Когда не найдено совпадений, выводится предупреждение в логах"""
    operations = [
        {"Описание": "Оплата счета", "Категория": "ЖКХ"},
        {"Описание": "Перевод на карту", "Категория": "Трансакции"}
    ]
    search_string = "погашение кредита"

    with patch('src.services.logger') as mock_logger:
        result = get_sort_bank_operations(operations, search_string)

        # Проверяем, что лог был записан как предупреждение
        mock_logger.warning.assert_called_once_with("Не найдено совпадений для строки поиска: 'погашение кредита'")

    assert len(result) == 0
