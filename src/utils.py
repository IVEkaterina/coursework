import pandas as pd

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
