import logging
from functools import wraps

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

log_file_path = BASE_DIR / 'logs' / 'decorators.log'

log_file_path.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def decorator_record_file(file_name):
    """
    Декоратор, который записывает результат выполнения функции в JSON файл. Принимает на вход имя файла.
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):

            df = func(*args, **kwargs)

            logger.info('Проверка: являются ли данные датафреймом')

            if isinstance(df, pd.DataFrame):

                logger.info('Запись отчёта в файл')

                df.to_json(file_name, orient="records", lines=True, force_ascii=False)

            else:
                logger.error('Данные не являются датафреймом. В файл записаны не будут')

            return df

        return inner

    return wrapper