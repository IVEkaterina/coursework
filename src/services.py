import re
import logging


logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('../logs/services.log')
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

def get_sort_bank_operations(operations: list[dict], search_string: str) -> list[dict]:
    """Функция, которая принимает список словарей с данными о банковских операциях и строку поиска,
    а потом фильтрует операции по строке поиска в описании или категории. И возвращает список словарей операций, где это слово совпало"""
    logger.info(f"Получена строка:'{search_string}', для фильлтрации")
    try:
        logger.info("Успешно началась обработка операций")
        pattern = re.compile(search_string, re.I)
        result = []

        for oper in operations:
            logger.debug(f"Обработка операции: {oper}")
            description = str(oper.get("Описание", "") or "")
            category = str(oper.get("Категория", "") or "")

            if pattern.search(description) or pattern.search(category):
                logger.info(f"Найдено совпадение для операции: {oper}")
                result.append(oper)
        if  result == []:
            logger.warning(f"Не найдено совпадений для строки поиска: '{search_string}'")

        return result
    except Exception as e:
        logger.error(f"Ошибка при обработке транзакций: {str(e)}", exc_info=True)
        return []
