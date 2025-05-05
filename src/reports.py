import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd

from src.decorators import decorator_record_file

BASE_DIR = Path(__file__).resolve().parents[1]

log_file_path = BASE_DIR / 'logs' / 'reports.log'

log_file_path.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.propagate = False

logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


@decorator_record_file('result.txt')
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция принимает на вход:
            -датафрейм с транзакциями,
            -название категории,
            -опциональную дату.

            Если дата не передана, то берется текущая дата.
            Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)."""
    try:
        logger.info('Если дата не передана, то берется текущая дата')
        if not date:
            stop_date = datetime.now()
        else:
            stop_date = datetime.strptime(date, "%d.%m.%Y")

        pattern = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})")
        result_sort_date = []

        if pattern.fullmatch(stop_date.strftime("%d.%m.%Y")):
            start_date = stop_date - timedelta(days=90)
            for transaction in transactions.to_dict('records'):
                operation_date_obj = datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S").date()
                if start_date.date() <= operation_date_obj <= stop_date.date():
                    result_sort_date.append(transaction)

        result_sort = []

        for result in result_sort_date:
            if (category == result["Категория"]) and (result["Сумма платежа"] < 0) and (result["Статус"] == "OK"):
                result_sort.append(result)

        logger.info('Все успешно')
        return pd.DataFrame(result_sort)

    except Exception:
        logger.error('Произошла ошибка')
        return pd.DataFrame({})
