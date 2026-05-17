"""Модуль ввода-вывода для чтения файлов разных форматов."""
from app.io.reader_registry import ReaderRegistry
from app.io.csv_reader import CSVReader
from app.io.json_reader import JSONReader


def setup_registry() -> ReaderRegistry:
    """
    Создаёт и настраивает реестр читателей.

    Returns:
        Настроенный экземпляр ReaderRegistry
    """
    registry = ReaderRegistry()
    registry.register('.csv', CSVReader)
    registry.register('.json', JSONReader)
    return registry
