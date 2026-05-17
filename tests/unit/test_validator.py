"""Unit-тесты для валидатора."""
import pytest
from app.services.validator import Validator
from app.core.models import Transaction


class TestValidator:
    """Тесты для класса Validator."""

    @pytest.mark.parametrize("amount, expected_valid", [
        (100.50, True),      # валидная сумма
        (0.01, True),        # минимальная валидная сумма
        (0, False),          # ноль -> невалидно
        (-1.0, False),       # отрицательная -> невалидно
        (-100.50, False),    # большая отрицательная -> невалидно
        ("abc", False),      # строка -> невалидно
        ("", False),         # пустая строка -> невалидно
        (999999999.99, True),  # очень большое число -> валидно
    ])
    def test_amount_validation(self, validator, amount, expected_valid):
        """Проверка валидации суммы."""
        record = {
            "id": "1",
            "amount": amount,
            "category": "Food",
            "date": "2024-01-15"
        }
        result = validator.validate_record(record, "test.csv")
        assert result == expected_valid

    @pytest.mark.parametrize("date_str, expected_valid", [
        ("2024-01-15", True),   # правильный формат
        ("2024-12-31", True),   # правильный формат
        ("2024/01/15", False),  # слеши вместо дефисов
        ("15-01-2024", False),  # день перед месяцем
        ("2024-01", False),     # только год и месяц
        ("2024-13-01", False),  # несуществующий месяц
        ("2024-01-32", False),  # несуществующий день
        ("", False),            # пустая строка
        ("abc", False),         # не дата
    ])
    def test_date_validation(self, validator, date_str, expected_valid):
        """Проверка валидации даты."""
        record = {
            "id": "1",
            "amount": 100.50,
            "category": "Food",
            "date": date_str
        }
        result = validator.validate_record(record, "test.csv")
        assert result == expected_valid

    @pytest.mark.parametrize("category, expected_valid", [
        ("Food", True),        # нормальная категория
        ("Transport", True),   # нормальная категория
        ("", False),           # пустая строка
        ("   ", False),        # только пробелы
    ])
    def test_category_validation(self, validator, category, expected_valid):
        """Проверка валидации категории."""
        record = {
            "id": "1",
            "amount": 100.50,
            "category": category,
            "date": "2024-01-15"
        }
        result = validator.validate_record(record, "test.csv")
        assert result == expected_valid

    @pytest.mark.parametrize("missing_field", ["id", "amount", "category", "date"])
    def test_missing_fields(self, validator, missing_field):
        """Проверка: запись с отсутствующим полем."""
        record = {
            "id": "1",
            "amount": 100.50,
            "category": "Food",
            "date": "2024-01-15"
        }
        del record[missing_field]

        result = validator.validate_record(record, "test.csv")
        assert result is False

        # Проверяем, что ошибка залогирована
        assert len(validator.errors) == 1
        assert f"Отсутствует поле: {missing_field}" in validator.errors[0][1]

    def test_valid_record_creates_transaction(self, validator):
        """Проверка: валидная запись создаёт объект Transaction."""
        record = {
            "id": "123",
            "amount": 75.50,
            "category": "Books",
            "date": "2024-01-20"
        }

        result = validator.validate_record(record, "test.csv")

        assert result is True
        assert len(validator.valid_transactions) == 1

        transaction = validator.valid_transactions[0]
        assert transaction.id == "123"
        assert transaction.amount == 75.50
        assert transaction.category == "Books"
        assert transaction.date == "2024-01-20"
        assert transaction.source_file == "test.csv"

    def test_multiple_records_validation(self, validator):
        """Проверка: валидация нескольких записей."""
        records = [
            {"id": "1", "amount": 100, "category": "Food", "date": "2024-01-01"},
            {"id": "2", "amount": -50, "category": "Transport", "date": "2024-01-02"},
            {"id": "3", "amount": 200, "category": "", "date": "2024-01-03"},
            {"id": "4", "amount": 300, "category": "Rent", "date": "2024-01-04"},
        ]

        for record in records:
            validator.validate_record(record, "test.csv")

        # 2 валидные записи (1 и 4), 2 ошибки
        assert len(validator.valid_transactions) == 2
        assert len(validator.errors) == 2

    def test_clear_method(self, validator):
        """Проверка: метод clear очищает результаты."""
        record = {"id": "1", "amount": 100, "category": "Food", "date": "2024-01-01"}
        validator.validate_record(record, "test.csv")

        assert len(validator.valid_transactions) == 1
        assert len(validator.errors) == 0

        validator.clear()

        assert len(validator.valid_transactions) == 0
        assert len(validator.errors) == 0

    def test_get_error_summary(self, validator):
        """Проверка: метод get_error_summary возвращает правильную сводку."""
        record1 = {"id": "1", "amount": -10, "category": "Food", "date": "2024-01-01"}
        record2 = {"id": "2", "amount": "abc", "category": "Food", "date": "2024-01-01"}

        validator.validate_record(record1, "test.csv")
        validator.validate_record(record2, "test.csv")

        summary = validator.get_error_summary()

        assert summary['total_errors'] == 2
        assert len(summary['errors']) == 2
