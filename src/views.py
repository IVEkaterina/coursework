import logging
import datetime
from pathlib import Path
from dotenv import load_dotenv

from src.utils import (
    get_card_info,
    get_currency_rates,
    get_stock_prices,
    get_top_transactions,
    greetings,
    load_user_settings,
    read_transactions_from_excel,
    sort_by_date,
)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]

log_file_path = BASE_DIR / 'logs' / 'views.log'

log_file_path.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.propagate = False

logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def main_func_for_views(datetime_str: str) -> dict:
    """
        Главная функция. Принимает строку с датой и временем в формате "YYYY-MM-DD HH:MM:SS".

        Возвращает JSON-объект в формате:
        {"greeting": приветствие,
            "cards": [{
              "last_digits": последние 4 цифры карты,
              "total_spent": общая сумма расходов,
              "cashback": кешбэк (1 рубль на каждые 100 рублей)
            }],
            "top_transactions": [{
              "date": дата операции,
              "amount": сумма операции,
              "category": категория операции,
              "description": описание операции
            }],
            "currency_rates": [{
              "currency": валюта,
              "rate": курс валюты в рублях
            }],
            "stock_prices": [{
              "stock": акция,
              "price": цена акции
            }]
        }
        """
    try:
        logger.debug("Определяю все переменные и записываю их в словарь")
        dt = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        operations = read_transactions_from_excel("../data/operations.xlsx")
        user_settings = load_user_settings()

        dt_day = datetime.datetime.strftime(dt, "%d.%m.%Y")

        operations_sort = sort_by_date(operations, dt_day)

        time = datetime.datetime.now()
        time_now = str(time.strftime("%H:%M:%S"))
        greeting = greetings(time_now)
        card_info = get_card_info(operations_sort)
        top_operations = get_top_transactions(operations_sort)
        currency_rates = get_currency_rates(user_settings['user_currencies'])
        stock_prices = get_stock_prices(user_settings['user_stocks'])

        response = {"greeting": greeting,
                    "cards": card_info,
                    "top_transactions": top_operations,
                    "currency_rates": currency_rates,
                    "stock_prices": stock_prices}

        return response
    except ValueError:
        logger.error("Неверный формат даты. Используйте YYYY-MM-DD HH:MM:SS")
        return {}
