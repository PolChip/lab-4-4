"""Реализация читателя CSV-файлов."""
import csv
from pathlib import Path
from typing import List, Dict, Any

from app.io.reader_registry import FileReader
from app.core.exceptions import (
    DataFormatError, FileAccessError, EmptyFileError
)


class CSVReader(FileReader):
    """Читает CSV-файлы с заголовком."""

    def read(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Читает CSV и возвращает список словарей.

        Ожидается, что файл имеет заголовок с колонками:
        id, amount, category, date
        """
        records = []

        # Проверка: файл не пустой
        if file_path.stat().st_size == 0:
            raise EmptyFileError(f"Файл {file_path.name} пустой")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                if reader.fieldnames is None:
                    raise DataFormatError(
                        f"CSV файл {file_path.name} не имеет строки заголовка"
                    )

                for row_num, row in enumerate(reader, start=2):
                    if all(v == '' or v is None for v in row.values()):
                        continue

                    required_fields = {'id', 'amount', 'category', 'date'}
                    missing_fields = required_fields - set(row.keys())
                    if missing_fields:
                        raise DataFormatError(
                            f"CSV {file_path.name} отсутствуют колонки: "
                            f"{missing_fields}"
                        )

                    records.append(row)

        except csv.Error as e:
            raise DataFormatError(
                f"Ошибка парсинга CSV в {file_path.name}: {e}"
            )
        except PermissionError as e:
            raise FileAccessError(
                f"Нет прав на чтение файла {file_path.name}: {e}"
            )
        except OSError as e:
            raise FileAccessError(
                f"Ошибка доступа к файлу {file_path.name}: {e}"
            )

        return records
