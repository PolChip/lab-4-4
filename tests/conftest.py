"""Общие фикстуры для pytest."""
import pytest
import json
from pathlib import Path
from app.services.validator import Validator
from app.services.aggregator import Aggregator
from app.core.models import Transaction


@pytest.fixture
def validator():
    """Фикстура: создаёт чистый экземпляр валидатора."""
    return Validator()


@pytest.fixture
def aggregator():
    """Фикстура: создаёт чистый экземпляр агрегатора."""
    return Aggregator(strict_duplicate_check=False)


@pytest.fixture
def strict_aggregator():
    """Фикстура: агрегатор в строгом режиме (с выбросом исключений)."""
    return Aggregator(strict_duplicate_check=True)


@pytest.fixture
def sample_transaction():
    """Фикстура: пример валидной транзакции."""
    return Transaction(
        id="test1",
        amount=100.50,
        category="Food",
        date="2024-01-15",
        source_file="test.csv"
    )


@pytest.fixture
def temp_csv_file(tmp_path):
    """Фикстура: создаёт временный CSV файл."""
    def _create_csv(content: str, filename: str = "test.csv") -> Path:
        file_path = tmp_path / filename
        file_path.write_text(content, encoding='utf-8')
        return file_path
    return _create_csv


@pytest.fixture
def temp_json_file(tmp_path):
    """Фикстура: создаёт временный JSON файл."""
    def _create_json(data, filename: str = "test.json") -> Path:
        file_path = tmp_path / filename
        file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        return file_path
    return _create_json