import json
import os
import re
from typing import Any, cast
from pathlib import Path
import requests
import pandas as pd
from datetime import datetime, time, timedelta
import logging

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]

log_file_path = BASE_DIR / 'logs' / 'utils.log'

log_file_path.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

def read_transactions_from_excel(file_path: str) -> list[dict]:
    """Считывает XLSX-файл с финансовыми операциями и возвращает список словарей.

        Аргументы:
            file_path (str): Путь к Excel-файлу (.xlsx).

        Возвращает:
            list[dict]: Список словарей, каждый из которых представляет одну финансовую операцию.

        Исключения:
            UnicodeDecodeError: Ошибка кодировки при чтении файла.
            FileNotFoundError: Если указанный файл не найден.
            Exception: Любая другая ошибка при чтении файла.
        """
    try:
        df = pd.read_excel(file_path)
        return df.to_dict(orient="records")
    except UnicodeDecodeError as ex:
        print(f"Ошибка кодировки: {ex}")
    except FileNotFoundError:
        print(f"Файл не найден: {file_path}")
    except Exception as ex:
        print(f"Произошла ошибка: {ex}")
    return []


def greetings(actual_time: str) -> str:
    """
    Функция, принимающая время в виде строки в формате HH:MM:SS
    и возвращающая приветствие в зависимости от времени суток.
    """
    try:

        logger.info("Из переданной строки с датой создаем DataFrame")

        date_obj = datetime.strptime(actual_time, "%H:%M:%S")

        greets = ["Доброе утро!", "Добрый день!", "Добрый вечер!", "Доброй ночи!"]

        comparison_night = time(0, 0)
        comparison_morning = time(4, 0)
        comparison_day = time(12, 0)
        comparison_evening = time(16, 0)

        logger.info("Определяем какое приветствие подойдет для текущего времени суток")

        if comparison_night <= date_obj.time() < comparison_morning:
            greet = greets[3]

        elif comparison_morning <= date_obj.time() < comparison_day:
            greet = greets[0]

        elif comparison_day <= date_obj.time() < comparison_evening:
            greet = greets[1]

        else:
            greet = greets[2]

        logger.info("Приветствие определено успешно")

        return greet

    except ValueError:

        logger.error("Передано неверное время")

        raise ValueError("Неверный формат времени")


def sort_by_date(operations: list[dict], input_date: str) -> str | list[dict]:
    """
    Функция, получающая список словарей с операциями и дату, возвращающая список, отфильтрованный
    по дате с начала месяца, на который выпадает входящая дата, по входящую дату.
    """
    pattern = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})")

    result = []

    logger.info("Проверяем переданную дату на корректный формат")

    if input_date and pattern.fullmatch(input_date):

        logger.info("Формат даты корректный")

        day_int = int(input_date[:2])

        input_date_obj = datetime.strptime(input_date, "%d.%m.%Y").date()

        start = input_date_obj - timedelta(days=(day_int - 1))
        stop = input_date_obj
        logger.info("Фильтруем операции по дате")
        for operation in operations:
            operation_date_obj = datetime.strptime(operation["Дата операции"], "%d.%m.%Y %H:%M:%S").date()

            if start <= operation_date_obj <= stop:
                result.append(operation)

    else:

        logger.warning("Введена неверная дата")

        print("Введена неверная дата. Введите дату в формате ДД.ММ.ГГГГ")

    return result


def get_card_info(operations_list: list[dict]) -> list[dict]:
    """
    Функция, принимающая список операций и возвращающая список словарей с данными о картах:
    последние 4 цифры карты, общая сумма расходов, кешбэк (1 рубль на каждые 100 рублей) в формате
    [{"last_digits": "4 последние цифры номера карты",
      "total_spent": сумма расходов,
      "cashback": кэшбек},
    {...}]
    """
    card_data = {}
    pattern = re.compile(r"\*\d{4}")

    logger.info("Определяем номер карты")
    for operation in operations_list:

        if isinstance(operation["Номер карты"], str) and pattern.fullmatch(operation["Номер карты"]):
            if "Сумма операции" in operation and "Статус" in operation:

                card_number = operation["Номер карты"][1:]
                amount = operation["Сумма операции"]

                logger.info("Проверяем статус каждой операции")

                if operation["Статус"] == "OK" and float(amount) < 0:
                    if card_number not in card_data:
                        logger.info("Считаем сумму операций по каждой карте")

                        card_data[card_number] = 0.0

                    card_data[card_number] += abs(float(amount))

    result = []

    logger.info("Формируем результат с данными о картах")

    for card_num, data in card_data.items():
        last_digits = card_num
        total_spent = data
        cashback = total_spent * 0.01

        result.append(
            {"last_digits": last_digits, "total_spent": round(total_spent, 2), "cashback": round(cashback, 2)}
        )

    return result


def get_top_transactions(operations: list[dict]) -> list[dict]:
    """
    Функция, принимающая список словарей с операциями и возвращающая список из топ-5 транзакций по сумме
    в формате:
    [{"date": "дата",
      "amount": сумма,
      "category": "категория",
      "description": "описание"},
    {...}]
    """
    result = []

    negative_transactions = [
        operation for operation in operations if "Сумма операции" in operation and operation["Сумма операции"] < 0
    ]

    logger.info("Определяем топ-5 операций по сумме")

    top_5 = sorted(negative_transactions, key=lambda x: abs(x["Сумма операции"]), reverse=True)[:5]

    logger.info("Формируем данные для получения топ-5 операций в нужном формате")

    for top in top_5:
        date = top["Дата операции"].split()[0]
        amount = abs(top["Сумма операции"])
        category = top["Категория"]
        description = top["Описание"]

        info_top = {"date": date, "amount": round(amount, 2), "category": category, "description": description}
        result.append(info_top)

    return result


def load_user_settings(filepath: str = '../user_settings.json') -> dict[Any, Any]:
    """Функция, которая загружает настройки пользователя из указанного JSON-файла, принимая Путь к файлу и
    возвращая словарь, содержащий данные, считанные из JSON-файла"""
    with open(filepath, 'r', encoding='utf-8') as file:
        return cast(dict[Any, Any], json.load(file))


def get_currency_rates(currencies: list[str]) -> list[dict]:
    """Функция, которая принемает на вход список валют и возвращает курс этих валют"""
    try:
        api_key = os.getenv("CURRENCY_API_KEY")
        if not api_key:
            logging.error("API ключ не найден в переменных окружения")
            return []

        url = f"https://api.currencyapi.com/v3/latest?apikey={api_key}"
        logging.info(f"Отправка запроса на: {url}")
        response = requests.get(url)
        result = response.json()

        data = result.get("data", {})
        rub_value = data.get("RUB", {}).get("value")

        if not rub_value:
            logger.warning("Значение RUB не найдено в данных ответа")
            return []

        results = []
        for code in currencies:
            currency_data = data.get(code)
            if currency_data:
                currency_value = currency_data.get("value")
                if currency_value and currency_value != 0:
                    rate_to_rub = round(rub_value / currency_value, 2)
                    results.append({"currency": code, "rate": rate_to_rub})
                else:
                    logger.warning(f"Пустое или нулевое значение для валюты {code}")
            else:
                logger.warning(f"Валюта {code} не найдена в ответе API")

        return results
    except Exception as e:
        logger.error(f"В ходе выполнения произошла ошибка: {e}")
        return []


def get_stock_prices(stocks: list[str]) -> list[dict]:
    """Функция, которая принемает на вход список названий акций из S&P500 и возвращает каждой ее стоимость"""
    api_key = os.getenv("STOCK_API_KEY")
    if not api_key:
        logging.error("API ключ не найден в переменных окружения")
        return []
    url = "https://finnhub.io/api/v1/quote"
    headers = {
        "X-Finnhub-Token": api_key
    }

    result = []
    for stock in stocks:
        logging.info(f"Отправка запроса на: {url}")
        response = requests.get(url, params={"symbol": stock}, headers=headers)
        data = response.json()
        price = data.get("c")
        if price:
            result.append({
                "stock": stock,
                "price": round(price, 2)
            })
        else:
            logger.warning("Стоимости на акцию нет")
    return result
