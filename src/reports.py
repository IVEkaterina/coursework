from datetime import datetime
import datetime
import logging
import pandas as pd
from typing import Optional
from src.decorators import decorator_record_file

my_logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('../logs/reports_logs.log', 'w')
file_formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
file_handler.setFormatter(file_formatter)
my_logger.addHandler(file_handler)
my_logger.setLevel(logging.DEBUG)


@decorator_record_file('result.txt')
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    try:
        my_logger.info('Если дата не передана, то берется текущая дата')
        if not date:
            stop_date = datetime.now()
        else:
            stop_date = datetime.strptime(date, "%d.%m.%Y")

        start_date = stop_date - datetime.timedelta(days=90)
        columns = ['Дата платежа', 'Сумма операции', 'Категория']
        my_logger.info('Проверяем наличие необходимых нам колонок')
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
        my_logger.info('Все успешно')
        return result
    except Exception:
        my_logger.error('Произошла ошибка')
        return pd.DataFrame({})