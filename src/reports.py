from datetime import datetime
import datetime
import logging
import pandas as pd
from typing import Optional
from src.decorators import decorator_record_file
from pathlib import Path
from pprint import pprint

from src.utils import read_transactions_from_excel

BASE_DIR = Path(__file__).resolve().parents[1]

log_file_path = BASE_DIR / 'logs' / 'reports.log'

log_file_path.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

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
        start_date = stop_date - datetime.timedelta(days=90)
        columns = ['Дата платежа', 'Сумма операции', 'Категория']
        logger.info('Проверяем наличие необходимых нам колонок')
        for i in columns:
            if i not in transactions.columns:
                return pd.DataFrame()
        transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y")
        filtered_transactions = transactions[(transactions["Дата платежа"] >= start_date) & (transactions["Дата платежа"] <= stop_date) &
                                             (transactions["Категория"] == category) &
                                             (transactions["Сумма операции"] < 0)]
        spending = abs(filtered_transactions["Сумма операции"])
        result = pd.DataFrame({
            "Категория": [category] * len(spending),
            "Сумма трат": spending
        })
        logger.info('Все успешно')
        return result
    except Exception:
        logger.error('Произошла ошибка')
        return pd.DataFrame({})

tr = read_transactions_from_excel("../data/operations.xlsx")
pprint(spending_by_category(tr, "переводы", "19.06.2019"))