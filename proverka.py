from datetime import datetime, timedelta
import re
from pprint import pprint
from src.utils import read_transactions_from_excel


def spending_by_category(transactions, category, date=None):
    if not date:
        stop_date = datetime.now()
    else:
        stop_date = datetime.strptime(date, "%d.%m.%Y")

    pattern = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})")
    result_sort_date = []

    if pattern.fullmatch(stop_date.strftime("%d.%m.%Y")):
        start_date = stop_date - timedelta(days=90)
        for transaction in transactions:
            operation_date_obj = datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S").date()

            if start_date.date() <= operation_date_obj <= stop_date.date():
                result_sort_date.append(transaction)

    result_sort = []

    for result in result_sort_date:
        if (category == result["Категория"]) and (result["Сумма платежа"] < 0) and (result["Статус"] == "OK"):
            result_sort.append(result)

    return result_sort


tr = read_transactions_from_excel("./data/operations.xlsx")
pprint(spending_by_category(tr, "Другое", "23.12.2021"))
