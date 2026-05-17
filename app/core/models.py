"""Модели данных для финансовых транзакций."""
from dataclasses import dataclass
from typing import Any


@dataclass
class Transaction:
    """Представляет одну финансовую транзакцию."""
    id: str              # Уникальный идентификатор транзакции
    amount: float        # Сумма (должна быть положительной)
    category: str        # Категория расхода/дохода
    date: str            # Дата в формате ISO YYYY-MM-DD
    source_file: str     # Имя файла-источника

    def to_dict(self) -> dict[str, Any]:
        """Преобразует транзакцию в словарь для JSON-сериализации."""
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
            "source_file": self.source_file
        }
