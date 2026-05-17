"""Unit-тесты для моделей данных."""
from app.core.models import Transaction


class TestTransaction:
    """Тесты для класса Transaction."""

    def test_transaction_creation(self):
        """Проверка создания транзакции."""
        transaction = Transaction(
            id="test1",
            amount=100.50,
            category="Food",
            date="2024-01-15",
            source_file="test.csv"
        )

        assert transaction.id == "test1"
        assert transaction.amount == 100.50
        assert transaction.category == "Food"
        assert transaction.date == "2024-01-15"
        assert transaction.source_file == "test.csv"

    def test_transaction_to_dict(self):
        """Проверка преобразования транзакции в словарь."""
        transaction = Transaction(
            id="test1",
            amount=100.50,
            category="Food",
            date="2024-01-15",
            source_file="test.csv"
        )

        result = transaction.to_dict()

        assert result == {
            "id": "test1",
            "amount": 100.50,
            "category": "Food",
            "date": "2024-01-15",
            "source_file": "test.csv"
        }

    def test_transaction_with_string_amount(self):
        """Проверка: amount хранится как float, даже если передан строкой."""
        transaction = Transaction(
            id="test1",
            amount=100.50,
            category="Food",
            date="2024-01-15",
            source_file="test.csv"
        )

        assert isinstance(transaction.amount, float)
        assert transaction.amount == 100.50
