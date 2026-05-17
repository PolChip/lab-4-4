"""Сервис валидации данных."""
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime

from app.core.models import Transaction

logger = logging.getLogger(__name__)


class Validator:
    """Валидатор записей транзакций."""

    def __init__(self):
        self.errors: List[Tuple[str, str]] = []
        self.valid_transactions: List[Transaction] = []

    def validate_record(
        self, record: Dict[str, Any], source_file: str
    ) -> bool:
        """
        Валидирует одну запись.

        Returns:
            True если запись валидна, False если невалидна
        """
        record_id = record.get('id', 'unknown')
        record_identifier = f"{source_file}:{record_id}"

        required_fields = ['id', 'amount', 'category', 'date']
        for field in required_fields:
            if field not in record:
                self.errors.append(
                    (record_identifier, f"Отсутствует поле: {field}")
                )
                return False

        try:
            amount = float(record['amount'])
            if amount <= 0:
                self.errors.append((
                    record_identifier,
                    f"Сумма должна быть > 0, получено {amount}"
                ))
                return False
        except (ValueError, TypeError):
            self.errors.append((
                record_identifier,
                f"Неверный формат суммы: {record['amount']}"
            ))
            return False

        try:
            datetime.strptime(record['date'], '%Y-%m-%d')
        except ValueError:
            self.errors.append((
                record_identifier,
                f"Неверный формат даты: {record['date']} "
                f"(ожидается YYYY-MM-DD)"
            ))
            return False

        if not record['category'] or not str(record['category']).strip():
            self.errors.append(
                (record_identifier, "Категория не может быть пустой")
            )
            return False

        transaction = Transaction(
            id=str(record['id']),
            amount=amount,
            category=str(record['category']).strip(),
            date=record['date'],
            source_file=source_file
        )
        self.valid_transactions.append(transaction)
        return True

    def validate_file_records(
        self, records: List[Dict[str, Any]], source_file: str
    ) -> List[Transaction]:
        """Валидирует все записи из файла."""
        for record in records:
            self.validate_record(record, source_file)
        return self.valid_transactions

    def get_error_summary(self) -> Dict[str, Any]:
        """Возвращает сводку ошибок валидации."""
        return {
            'total_errors': len(self.errors),
            'errors': self.errors
        }

    def clear(self) -> None:
        """Очищает результаты валидации."""
        self.errors.clear()
        self.valid_transactions.clear()
