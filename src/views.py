import json
import requests
import pandas as pd
from datetime import datetime, time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('../logs/views.log')
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


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
