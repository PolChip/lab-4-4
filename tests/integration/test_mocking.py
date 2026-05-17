"""Тесты с использованием mocking для имитации системных ошибок."""
import pytest
from unittest.mock import patch
from pathlib import Path
from app.core.models import Transaction


class TestMocking:
    """Тесты с использованием mock объектов."""

    @patch('app.services.aggregator.logger')
    def test_duplicate_id_logging(self, mock_logger, aggregator):
        """Mocking: проверка логирования дубликатов ID."""
        t1 = Transaction("dup1", 100, "Food", "2024-01-01", "file1.csv")
        t2 = Transaction("dup1", 200, "Transport", "2024-01-02", "file1.csv")

        aggregator.add_transaction(t1)
        aggregator.add_transaction(t2)

        mock_logger.warning.assert_called()
        assert "Дубликат ID" in mock_logger.warning.call_args[0][0]

    @patch('builtins.open')
    def test_file_write_error_handling(self, mock_open, aggregator):
        """Mocking: имитация ошибки записи файла."""
        mock_open.side_effect = OSError("No space left on device")

        transaction = Transaction("1", 100, "Food", "2024-01-01", "test.csv")
        aggregator.add_transaction(transaction)

        results = aggregator.get_results()
        assert results['total_transactions'] == 1
        assert results['total_amount'] == 100

    def test_csv_permission_error(self, tmp_path):
        """Тест: имитация ошибки PermissionError при чтении CSV.

        Создаёт реальный файл и убирает права на чтение через chmod.
        """
        from app.io.csv_reader import CSVReader
        from app.core.exceptions import FileAccessError

        # Создаём временный CSV файл
        test_file = tmp_path / "test.csv"
        test_file.write_text(
            "id,amount,category,date\n"
            "1,100.50,Food,2024-01-15\n"
            "2,200.00,Transport,2024-01-16",
            encoding='utf-8'
        )

        # Убираем права на чтение
        test_file.chmod(0o000)

        reader = CSVReader()

        try:
            with pytest.raises(FileAccessError) as exc_info:
                reader.read(test_file)

            assert "прав" in str(exc_info.value) or "Permission" in str(exc_info.value)
        finally:
            # Возвращаем права, чтобы файл можно было удалить
            test_file.chmod(0o644)

    def test_json_permission_error(self, tmp_path):
        """Тест: имитация ошибки PermissionError при чтении JSON.

        Создаёт реальный файл и убирает права на чтение через chmod.
        """
        from app.io.json_reader import JSONReader
        from app.core.exceptions import FileAccessError

        # Создаём временный JSON файл
        test_file = tmp_path / "test.json"
        test_file.write_text(
            '[\n'
            '    {"id": "1", "amount": 100.50, "category": "Food", "date": "2024-01-15"},\n'
            '    {"id": "2", "amount": 200.00, "category": "Transport", "date": "2024-01-16"}\n'
            ']',
            encoding='utf-8'
        )

        # Убираем права на чтение
        test_file.chmod(0o000)

        reader = JSONReader()

        try:
            with pytest.raises(FileAccessError) as exc_info:
                reader.read(test_file)

            assert "прав" in str(exc_info.value) or "Permission" in str(exc_info.value)
        finally:
            # Возвращаем права, чтобы файл можно было удалить
            test_file.chmod(0o644)

    @patch('shutil.move')
    @patch('builtins.open')
    def test_save_results_transactionally_error(
        self, mock_open, mock_move, aggregator, sample_transaction
    ):
        """Mocking: имитация ошибки при сохранении результата."""
        from main import save_results_transactionally

        mock_move.side_effect = OSError("Cannot move file")

        aggregator.add_transaction(sample_transaction)

        result = save_results_transactionally(aggregator, Path("result.json"))

        assert result is False

    @patch('app.services.aggregator.logger')
    def test_duplicate_id_warning_content(self, mock_logger, aggregator):
        """Mocking: проверка содержимого предупреждения о дубликате."""
        t1 = Transaction("dup1", 100, "Food", "2024-01-01", "file1.csv")
        t2 = Transaction("dup1", 200, "Transport", "2024-01-02", "file2.csv")

        aggregator.add_transaction(t1)
        aggregator.add_transaction(t2)

        call_args = mock_logger.warning.call_args[0][0]
        assert "dup1" in call_args
        assert "file1.csv" in call_args
        assert "file2.csv" in call_args
