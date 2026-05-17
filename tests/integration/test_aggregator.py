"""Интеграционные тесты для агрегатора."""
import pytest
from app.services.aggregator import Aggregator
from app.core.models import Transaction
from app.core.exceptions import DuplicateIdError


class TestAggregator:
    """Тесты для Aggregator."""

    def test_add_single_transaction(self, aggregator, sample_transaction):
        """Проверка добавления одной транзакции."""
        aggregator.add_transaction(sample_transaction)

        results = aggregator.get_results()
        assert results['total_transactions'] == 1
        assert results['total_amount'] == 100.50
        assert results['summary_by_category']['Food'] == 100.50

    def test_add_multiple_transactions_same_category(self, aggregator):
        """Проверка: несколько транзакций в одной категории суммируются."""
        t1 = Transaction("1", 100, "Food", "2024-01-01", "file1.csv")
        t2 = Transaction("2", 50, "Food", "2024-01-02", "file1.csv")
        t3 = Transaction("3", 75, "Food", "2024-01-03", "file1.csv")

        aggregator.add_transactions([t1, t2, t3])

        results = aggregator.get_results()
        assert results['total_transactions'] == 3
        assert results['total_amount'] == 225
        assert results['summary_by_category']['Food'] == 225

    def test_add_multiple_transactions_different_categories(self, aggregator):
        """Проверка: транзакции в разных категориях."""
        t1 = Transaction("1", 100, "Food", "2024-01-01", "file1.csv")
        t2 = Transaction("2", 200, "Transport", "2024-01-02", "file1.csv")
        t3 = Transaction("3", 300, "Rent", "2024-01-03", "file1.csv")

        aggregator.add_transactions([t1, t2, t3])

        results = aggregator.get_results()
        assert results['total_transactions'] == 3
        assert results['total_amount'] == 600
        assert results['summary_by_category']['Food'] == 100
        assert results['summary_by_category']['Transport'] == 200
        assert results['summary_by_category']['Rent'] == 300

    def test_duplicate_id_handling(self, aggregator):
        """Проверка: дубликат ID не создаёт новую транзакцию."""
        t1 = Transaction("dup1", 100, "Food", "2024-01-01", "file1.csv")
        t2 = Transaction("dup1", 200, "Transport", "2024-01-02", "file1.csv")

        aggregator.add_transaction(t1)
        aggregator.add_transaction(t2)

        results = aggregator.get_results()
        # Одна транзакция (последняя перезаписала первую)
        assert results['total_transactions'] == 1
        # Сумма последней транзакции
        assert results['summary_by_category']['Transport'] == 200

    def test_duplicate_id_tracking(self, aggregator):
        """Проверка: дубликаты ID отслеживаются."""
        t1 = Transaction("dup1", 100, "Food", "2024-01-01", "file1.csv")
        t2 = Transaction("dup2", 200, "Food", "2024-01-02", "file1.csv")
        t3 = Transaction("dup1", 300, "Food", "2024-01-03", "file1.csv")

        aggregator.add_transaction(t1)
        aggregator.add_transaction(t2)
        aggregator.add_transaction(t3)

        assert aggregator.get_duplicate_count() == 1
        assert "dup1" in aggregator.duplicate_ids

    def test_strict_mode_raises_exception(self, strict_aggregator):
        """Проверка: строгий режим выбрасывает DuplicateIdError."""
        t1 = Transaction("dup1", 100, "Food", "2024-01-01", "file1.csv")
        t2 = Transaction("dup1", 200, "Transport", "2024-01-02", "file1.csv")

        strict_aggregator.add_transaction(t1)

        with pytest.raises(DuplicateIdError) as exc_info:
            strict_aggregator.add_transaction(t2)

        assert "дубликат" in str(exc_info.value).lower() or "dup1" in str(exc_info.value)

    def test_clear_method(self, aggregator, sample_transaction):
        """Проверка: метод clear очищает результаты."""
        aggregator.add_transaction(sample_transaction)
        assert aggregator.get_results()['total_transactions'] == 1

        aggregator.clear()

        results = aggregator.get_results()
        assert results['total_transactions'] == 0
        assert results['total_amount'] == 0
        assert results['summary_by_category'] == {}
        assert aggregator.get_duplicate_count() == 0

    def test_full_integration_validator_aggregator(self, validator, aggregator):
        """Полный интеграционный тест: валидатор + агрегатор."""
        records = [
            {"id": "1", "amount": 100, "category": "Food", "date": "2024-01-01"},
            {"id": "2", "amount": -50, "category": "Food", "date": "2024-01-02"},
            {"id": "3", "amount": 200, "category": "Transport", "date": "2024-01-03"},
            {"id": "4", "amount": 0, "category": "Rent", "date": "2024-01-04"},
            {"id": "5", "amount": 300, "category": "Rent", "date": "2024-01-05"},
        ]

        for record in records:
            validator.validate_record(record, "test.csv")

        assert len(validator.valid_transactions) == 3

        for transaction in validator.valid_transactions:
            aggregator.add_transaction(transaction)

        results = aggregator.get_results()
        assert results['total_transactions'] == 3
        assert results['total_amount'] == 600  # 100 + 200 + 300
        assert results['summary_by_category']['Food'] == 100
        assert results['summary_by_category']['Transport'] == 200
        assert results['summary_by_category']['Rent'] == 300