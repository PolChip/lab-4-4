"""Реализация читателя JSON-файлов."""
import json
from pathlib import Path
from typing import List, Dict, Any

from app.io.reader_registry import FileReader
from app.core.exceptions import (
    DataFormatError, FileAccessError, EmptyFileError
)


class JSONReader(FileReader):
    """Читает JSON-файлы, содержащие массив объектов."""

    def read(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Читает JSON и возвращает список словарей.

        Поддерживает:
        - Прямой массив объектов: [{"id": 1, ...}, ...]
        - Объект с массивом внутри: {"transactions": [...], ...}
        """
        if file_path.stat().st_size == 0:
            raise EmptyFileError(f"Файл {file_path.name} пустой")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise DataFormatError(
                f"Неверный JSON в {file_path.name}: {e}"
            )
        except PermissionError as e:
            raise FileAccessError(
                f"Нет прав на чтение файла {file_path.name}: {e}"
            )
        except OSError as e:
            raise FileAccessError(
                f"Ошибка доступа к файлу {file_path.name}: {e}"
            )

        # Обработка формата: если JSON - объект с массивом внутри
        if isinstance(data, dict):
            for key in ['transactions', 'data', 'records']:
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break
            else:
                raise DataFormatError(
                    f"JSON {file_path.name}: ожидался массив, "
                    f"получен объект без массива данных"
                )

        if not isinstance(data, list):
            raise DataFormatError(
                f"JSON {file_path.name}: ожидался массив, "
                f"получен {type(data).__name__}"
            )

        required_fields = {'id', 'amount', 'category', 'date'}
        for i, record in enumerate(data):
            if not isinstance(record, dict):
                raise DataFormatError(
                    f"JSON {file_path.name}: запись {i} не является объектом"
                )

            missing_fields = required_fields - set(record.keys())
            if missing_fields:
                raise DataFormatError(
                    f"JSON {file_path.name} запись {i} "
                    f"не имеет полей: {missing_fields}"
                )

        return data
