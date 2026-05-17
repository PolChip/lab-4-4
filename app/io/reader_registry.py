"""Реестр (Registry Pattern) для обработчиков файлов разных форматов."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Type


class FileReader(ABC):
    """Абстрактный базовый класс для всех читателей файлов."""

    @abstractmethod
    def read(self, file_path: Path) -> List[dict]:
        """
        Читает файл и возвращает список сырых записей.

        Args:
            file_path: Путь к файлу

        Returns:
            Список словарей с данными из файла

        Raises:
            DataFormatError: Если файл повреждён или имеет неверный формат
        """
        pass


class ReaderRegistry:
    """Реестр для сопоставления расширений файлов с классами-читателями."""

    def __init__(self):
        self._readers: Dict[str, Type[FileReader]] = {}

    def register(self, extension: str, reader_class: Type[FileReader]) -> None:
        """
        Регистрирует читатель для определённого расширения файла.

        Args:
            extension: Расширение файла (например, '.csv')
            reader_class: Класс, реализующий FileReader
        """
        self._readers[extension.lower()] = reader_class

    def get_reader(self, file_path: Path) -> Type[FileReader]:
        """
        Возвращает класс-читатель для данного файла.

        Args:
            file_path: Путь к файлу

        Returns:
            Класс-читатель для данного расширения

        Raises:
            ValueError: Если для расширения не зарегистрирован читатель
        """
        extension = file_path.suffix.lower()
        if extension not in self._readers:
            raise ValueError(f"Нет читателя для расширения: {extension}")
        return self._readers[extension]
