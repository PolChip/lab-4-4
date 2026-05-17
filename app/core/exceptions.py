"""Иерархия пользовательских исключений для приложения."""


class BaseAppError(Exception):
    """Базовое исключение для всех ошибок приложения."""
    pass


class DataFormatError(BaseAppError):
    """Ошибка структуры файла (неверный формат, повреждённые данные)."""
    pass


class ValidationError(BaseAppError):
    """Ошибка бизнес-логики (например, отрицательная сумма)."""
    pass


class CurrencyMismatchError(BaseAppError):
    """Ошибка несоответствия валют (бонусное задание)."""
    pass


# Кастомные ошибки

class FileAccessError(BaseAppError):
    """
    Ошибка доступа к файлу.
    Возникает, когда файл:
    - заблокирован другим процессом
    - нет прав на чтение
    - является директорией, а не файлом
    """
    pass


class EmptyFileError(DataFormatError):
    """
    Ошибка: файл существует, но пустой.
    Наследуется от DataFormatError, так как это частный случай ошибки формата.
    """
    pass


class DuplicateIdError(ValidationError):
    """
    Ошибка: обнаружен дубликат ID транзакции.
    Наследуется от ValidationError, так как это ошибка бизнес-логики.
    """
    pass
