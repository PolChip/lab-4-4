"""Сервис агрегации данных."""
import logging
from typing import Dict, List, Any
from collections import defaultdict

from app.core.models import Transaction
from app.core.exceptions import DuplicateIdError

logger = logging.getLogger(__name__)


class Aggregator:
    """Агрегатор транзакций по категориям."""

    def __init__(self, strict_duplicate_check: bool = False):
        self.category_totals: Dict[str, float] = defaultdict(float)
        self.id_map: Dict[str, str] = {}
        self.duplicate_ids: List[str] = []
        self.strict_duplicate_check = strict_duplicate_check

    def add_transaction(self, transaction: Transaction) -> bool:
        """
        Добавляет транзакцию в агрегацию.

        Returns:
            True если добавлено, False если дубликат ID

        Raises:
            DuplicateIdError: Если strict_duplicate_check=True
        """
        if transaction.id in self.id_map:
            self.duplicate_ids.append(transaction.id)

            if self.strict_duplicate_check:
                raise DuplicateIdError(
                    f"Обнаружен дубликат ID '{transaction.id}'. "
                    f"Первый раз: {self.id_map[transaction.id]}, "
                    f"второй раз: {transaction.source_file}"
                )
            else:
                logger.warning(
                    f"Дубликат ID '{transaction.id}'. "
                    f"Первый раз: {self.id_map[transaction.id]}, "
                    f"второй раз: {transaction.source_file}"
                )

        self.id_map[transaction.id] = transaction.source_file
        self.category_totals[transaction.category] += transaction.amount
        return True

    def add_transactions(self, transactions: List[Transaction]) -> None:
        """Добавляет несколько транзакций."""
        for t in transactions:
            self.add_transaction(t)

    def get_results(self) -> Dict[str, Any]:
        """Возвращает результаты агрегации."""
        return {
            'summary_by_category': dict(self.category_totals),
            'total_transactions': len(self.id_map),
            'total_amount': sum(self.category_totals.values()),
            'categories': list(self.category_totals.keys()),
            'duplicate_ids': self.duplicate_ids
        }

    def get_duplicate_count(self) -> int:
        """Возвращает количество дубликатов ID."""
        return len(self.duplicate_ids)

    def clear(self) -> None:
        """Очищает результаты агрегации."""
        self.category_totals.clear()
        self.id_map.clear()
        self.duplicate_ids.clear()
