import logging
from pathlib import Path
from pprint import pprint

import pandas as pd

from src.reports import spending_by_category
from src.services import get_sort_bank_operations
from src.utils import read_transactions_from_excel
from src.views import main_func_for_views

BASE_DIR = Path(__file__).resolve().parents[1]
log_file_path = BASE_DIR / 'logs' / 'decorators.log'

log_file_path.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.propagate = False

logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

logger.info("Запрашивается дата для выполнения функции 'Главная'")
datetime_str = input("ВВедите дату в формате 'YYYY-MM-DD HH:MM:SS'").strip()
pprint(main_func_for_views(datetime_str))


logger.info("Получаем операции и запрашиваем слово поиска для функции 'Простой поиск'")
operations = read_transactions_from_excel("../data/operations.xlsx")

search_string = input("Введите слово по которой отфильтруются операции в описании или категории").strip()
pprint(get_sort_bank_operations(operations, search_string))


logger.info("Получаем операции в формате DataFrame и запрашиваем категорию и дату для функции 'Траты по категории'")
tr = pd.DataFrame(read_transactions_from_excel("../data/operations.xlsx"))

category = input("Введите категорию для фильтрации").strip()
date = input("Введите опциональную дату").strip()
pprint(spending_by_category(tr, category, date))
