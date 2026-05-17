"""Интеграционные тесты для JSON Reader."""
import pytest
from app.io.json_reader import JSONReader
from app.core.exceptions import DataFormatError


class TestJSONReader:
    """Тесты для JSONReader."""

    def test_read_valid_json_array(self, temp_json_file):
        """Проверка чтения валидного JSON массива."""
        data = [
            {"id": "1", "amount": 100.50, "category": "Food", "date": "2024-01-15"},
            {"id": "2", "amount": 200.00, "category": "Transport", "date": "2024-01-16"}
        ]

        file_path = temp_json_file(data, "valid.json")
        reader = JSONReader()
        records = reader.read(file_path)

        assert len(records) == 2
        assert records[0]["id"] == "1"
        assert records[0]["category"] == "Food"

    def test_read_valid_json_with_transactions_key(self, temp_json_file):
        """Проверка чтения JSON с объектом, содержащим массив по ключу."""
        data = {
            "transactions": [
                {"id": "1", "amount": 100.50, "category": "Food", "date": "2024-01-15"},
                {"id": "2", "amount": 200.00, "category": "Transport", "date": "2024-01-16"}
            ]
        }

        file_path = temp_json_file(data, "wrapped.json")
        reader = JSONReader()
        records = reader.read(file_path)

        assert len(records) == 2

    def test_read_empty_json(self, temp_json_file):
        """Проверка: пустой JSON файл вызывает DataFormatError."""
        file_path = temp_json_file("", "empty.json")
        reader = JSONReader()

        # Пустой файл не является валидным JSON, ожидаем DataFormatError
        with pytest.raises(DataFormatError):
            reader.read(file_path)

    def test_read_corrupt_json(self, tmp_path):
        """Проверка: битый JSON вызывает DataFormatError."""
        corrupt_path = tmp_path / "corrupt.json"
        corrupt_path.write_text('{"id": "1", "amount": 100', encoding='utf-8')

        reader = JSONReader()

        with pytest.raises(DataFormatError):
            reader.read(corrupt_path)

    def test_read_json_not_array(self, temp_json_file):
        """Проверка: JSON не массив и не объект с массивом вызывает ошибку."""
        data = {"id": "1", "amount": 100.50}

        file_path = temp_json_file(data, "not_array.json")
        reader = JSONReader()

        with pytest.raises(DataFormatError):
            reader.read(file_path)

    def test_mixed_json_validation(self, validator, temp_json_file):
        """Интеграционный тест: чтение JSON + валидация."""
        data = [
            {"id": "1", "amount": 100.50, "category": "Food", "date": "2024-01-15"},
            {"id": "2", "amount": 0, "category": "Transport", "date": "2024-01-16"},
            {"id": "3", "amount": 200.00, "category": "Rent", "date": "2024-01-17"}
        ]

        file_path = temp_json_file(data, "mixed.json")
        reader = JSONReader()

        records = reader.read(file_path)
        assert len(records) == 3

        for record in records:
            validator.validate_record(record, "mixed.json")

        # 2 валидные записи (1 и 3), 1 ошибка (сумма = 0)
        assert len(validator.valid_transactions) == 2
        assert len(validator.errors) == 1
