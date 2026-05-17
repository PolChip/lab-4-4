"""Интеграционные тесты для CSV Reader."""
import pytest
from pathlib import Path
from app.io.csv_reader import CSVReader
from app.io.reader_registry import ReaderRegistry
from app.core.exceptions import DataFormatError, EmptyFileError


class TestCSVReader:
    """Тесты для CSVReader."""

    def test_read_valid_csv(self, temp_csv_file):
        """Проверка чтения валидного CSV файла."""
        content = """id,amount,category,date
1,100.50,Food,2024-01-15
2,200.00,Transport,2024-01-16"""

        file_path = temp_csv_file(content, "valid.csv")
        reader = CSVReader()
        records = reader.read(file_path)

        assert len(records) == 2
        assert records[0]["id"] == "1"
        assert records[0]["amount"] == "100.50"
        assert records[0]["category"] == "Food"
        assert records[1]["id"] == "2"

    def test_read_empty_csv(self, temp_csv_file):
        """Проверка: пустой CSV файл вызывает EmptyFileError."""
        file_path = temp_csv_file("", "empty.csv")
        reader = CSVReader()

        with pytest.raises(EmptyFileError) as exc_info:
            reader.read(file_path)
        assert "пустой" in str(exc_info.value).lower()

    def test_read_csv_without_header(self, temp_csv_file):
        """Проверка: CSV без заголовка вызывает DataFormatError."""
        content = """1,100.50,Food,2024-01-15
2,200.00,Transport,2024-01-16"""

        file_path = temp_csv_file(content, "no_header.csv")
        reader = CSVReader()

        with pytest.raises(DataFormatError) as exc_info:
            reader.read(file_path)
        assert "заголовка" in str(exc_info.value) or "header" in str(exc_info.value).lower()

    def test_read_csv_missing_columns(self, temp_csv_file):
        """Проверка: CSV с отсутствующими колонками вызывает DataFormatError."""
        content = """id,amount,category
1,100.50,Food"""

        file_path = temp_csv_file(content, "missing_columns.csv")
        reader = CSVReader()

        with pytest.raises(DataFormatError) as exc_info:
            reader.read(file_path)
        assert "отсутствуют" in str(exc_info.value) or "missing" in str(exc_info.value).lower()

    def test_mixed_csv_with_good_and_bad_records(self, validator, temp_csv_file):
        """Интеграционный тест: чтение CSV + валидация."""
        content = """id,amount,category,date
1,100.50,Food,2024-01-15
2,-10.00,Food,2024-01-16
3,abc,Clothing,2024-01-17
4,200.00,Rent,2024-01-18"""

        file_path = temp_csv_file(content, "mixed.csv")
        reader = CSVReader()

        records = reader.read(file_path)
        assert len(records) == 4

        for record in records:
            validator.validate_record(record, "mixed.csv")

        # 2 валидные записи (1 и 4), 2 ошибки
        assert len(validator.valid_transactions) == 2
        assert len(validator.errors) == 2

    def test_registry_with_csv(self):
        """Проверка: реестр правильно возвращает CSVReader."""
        registry = ReaderRegistry()
        registry.register('.csv', CSVReader)

        reader_class = registry.get_reader(Path("test.csv"))
        assert reader_class == CSVReader
