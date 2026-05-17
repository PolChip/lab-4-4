"""Unit-тесты для кастомных исключений."""
import pytest
from app.core.exceptions import (
    BaseAppError,
    DataFormatError,
    ValidationError,
    FileAccessError,
    EmptyFileError,
    DuplicateIdError,
    CurrencyMismatchError
)


class TestCustomExceptions:
    """Тесты для кастомных исключений."""

    def test_base_app_error(self):
        """Проверка базового исключения."""
        with pytest.raises(BaseAppError):
            raise BaseAppError("Базовая ошибка")

    def test_data_format_error(self):
        """Проверка DataFormatError."""
        with pytest.raises(DataFormatError) as exc_info:
            raise DataFormatError("Ошибка формата файла")
        assert "Ошибка формата файла" in str(exc_info.value)
        assert issubclass(DataFormatError, BaseAppError)

    def test_validation_error(self):
        """Проверка ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("Ошибка бизнес-логики")
        assert "Ошибка бизнес-логики" in str(exc_info.value)
        assert issubclass(ValidationError, BaseAppError)

    def test_file_access_error(self):
        """Проверка FileAccessError."""
        with pytest.raises(FileAccessError) as exc_info:
            raise FileAccessError("Нет прав доступа")
        assert "Нет прав доступа" in str(exc_info.value)
        assert issubclass(FileAccessError, BaseAppError)

    def test_empty_file_error(self):
        """Проверка EmptyFileError (наследник DataFormatError)."""
        with pytest.raises(EmptyFileError) as exc_info:
            raise EmptyFileError("Файл пустой")
        assert "Файл пустой" in str(exc_info.value)
        assert issubclass(EmptyFileError, DataFormatError)
        assert issubclass(EmptyFileError, BaseAppError)

    def test_duplicate_id_error(self):
        """Проверка DuplicateIdError (наследник ValidationError)."""
        with pytest.raises(DuplicateIdError) as exc_info:
            raise DuplicateIdError("Дубликат ID")
        assert "Дубликат ID" in str(exc_info.value)
        assert issubclass(DuplicateIdError, ValidationError)
        assert issubclass(DuplicateIdError, BaseAppError)

    def test_currency_mismatch_error(self):
        """Проверка CurrencyMismatchError (бонус)."""
        with pytest.raises(CurrencyMismatchError) as exc_info:
            raise CurrencyMismatchError("Разные валюты")
        assert "Разные валюты" in str(exc_info.value)
        assert issubclass(CurrencyMismatchError, BaseAppError)

    def test_exception_hierarchy(self):
        """Проверка полной иерархии исключений."""
        exceptions = [
            DataFormatError,
            ValidationError,
            FileAccessError,
            EmptyFileError,
            DuplicateIdError,
            CurrencyMismatchError
        ]

        for exc in exceptions:
            assert issubclass(exc, BaseAppError)