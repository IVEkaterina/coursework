import pytest
from unittest.mock import patch
from src.services import get_sort_bank_operations


# Тест: Операции, соответствующие строке поиска
def test_get_sort_bank_operations_match():
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


# Тест: Нет совпадений для строки поиска
def test_get_sort_bank_operations_no_match():
    operations = [
        {"Описание": "Оплата счета", "Категория": "ЖКХ"},
        {"Описание": "Перевод на карту", "Категория": "Трансакции"},
        {"Описание": "Покупка в магазине", "Категория": "Товары"}
    ]
    search_string = "кредит"

    result = get_sort_bank_operations(operations, search_string)

    assert len(result) == 0


# Тест: Строки поиска не чувствительны к регистру
def test_get_sort_bank_operations_case_insensitive():
    operations = [
        {"Описание": "Оплата счета", "Категория": "ЖКХ"},
        {"Описание": "Перевод на карту", "Категория": "Трансакции"},
        {"Описание": "Покупка в магазине", "Категория": "Товары"}
    ]
    search_string = "ОПЛАТА"

    result = get_sort_bank_operations(operations, search_string)

    assert len(result) == 1
    assert result[0]["Описание"] == "Оплата счета"


# Тест: Операции без описания или категории
def test_get_sort_bank_operations_empty_description_or_category():
    operations = [
        {"Описание": "", "Категория": "ЖКХ"},
        {"Описание": "Перевод на карту", "Категория": ""},
        {"Описание": "Покупка в магазине", "Категория": "Товары"}
    ]
    search_string = "Перевод"

    result = get_sort_bank_operations(operations, search_string)

    assert len(result) == 1
    assert result[0]["Описание"] == "Перевод на карту"


# Тест: Пустой список операций
def test_get_sort_bank_operations_empty_operations():
    operations = []
    search_string = "оплата"

    result = get_sort_bank_operations(operations, search_string)

    assert len(result) == 0


# Тест: Ошибка при обработке данных (например, некорректный формат операций)


# Тест: Когда не найдено совпадений, выводится предупреждение в логах
def test_get_sort_bank_operations_warning_when_no_match():
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
