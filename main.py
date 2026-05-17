#!/usr/bin/env python3
"""Главная точка входа для Data Integration Engine."""
import sys
import logging
import json
import shutil
from pathlib import Path
from typing import List

from app.io import setup_registry
from app.services import Validator, Aggregator
from app.core.exceptions import (
    DataFormatError, FileAccessError, EmptyFileError, DuplicateIdError
)


def setup_logging() -> None:
    """Настраивает логирование в файл и консоль."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def scan_directory(data_dir: Path) -> List[Path]:
    """
    Сканирует директорию и возвращает список поддерживаемых файлов.
    """
    supported_extensions = {'.csv', '.json'}
    files = []

    for ext in supported_extensions:
        files.extend(data_dir.glob(f'*{ext}'))

    return sorted(files)


def process_file(
    file_path: Path,
    registry,
    validator: Validator
) -> tuple[int, int]:
    """
    Обрабатывает один файл.

    Returns:
        Кортеж (всего_записей, валидных_записей)
    """
    logger = logging.getLogger(__name__)

    try:
        reader_class = registry.get_reader(file_path)
        reader = reader_class()

        records = reader.read(file_path)
        logger.info(
            f"Прочитано {len(records)} записей из {file_path.name}"
        )

        valid_before = len(validator.valid_transactions)
        for record in records:
            validator.validate_record(record, file_path.name)

        valid_after = len(validator.valid_transactions)
        valid_count = valid_after - valid_before

        return len(records), valid_count

    except EmptyFileError as e:
        logger.warning(f"Пустой файл: {file_path.name} - {e}")
        return 0, 0
    except FileAccessError as e:
        logger.error(f"Ошибка доступа к файлу {file_path.name}: {e}")
        return 0, 0
    except DataFormatError as e:
        logger.error(f"Ошибка формата в {file_path.name}: {e}")
        return 0, 0
    except Exception as e:
        logger.error(
            f"Неожиданная ошибка при обработке {file_path.name}: {e}"
        )
        return 0, 0


def save_results_transactionally(
    aggregator: Aggregator, output_path: Path
) -> bool:
    """
    Сохраняет результаты с использованием транзакционной записи.
    """
    logger = logging.getLogger(__name__)

    results = aggregator.get_results()
    results['by_category_detailed'] = {
        category: {'total': amount}
        for category, amount in aggregator.category_totals.items()
    }
    results['id_sources'] = aggregator.id_map

    temp_path = output_path.parent / f"{output_path.name}.tmp"

    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        shutil.move(str(temp_path), str(output_path))
        logger.info(f"Результаты сохранены в {output_path}")
        return True

    except OSError as e:
        logger.error(f"Не удалось записать результаты: {e}")
        if temp_path.exists():
            temp_path.unlink()
        return False


def print_report(
    validator: Validator, aggregator: Aggregator, files_count: int
) -> None:
    """Выводит отчёт о выполнении в консоль."""
    print("Отчет об обработке")

    print(f"\nОбработано файлов: {files_count}")
    print(f"Валидных записей: {len(validator.valid_transactions)}")
    print(f"Ошибочных записей: {len(validator.errors)}")

    if aggregator.get_duplicate_count() > 0:
        print(f"Дубликатов ID: {aggregator.get_duplicate_count()}")

    if validator.errors:
        print("\nСписок ошибок (первые 10)")
        for i, (record_id, error) in enumerate(validator.errors[:10]):
            print(f"  {i+1}. {record_id}: {error}")
        if len(validator.errors) > 10:
            print(f"  ... и ещё {len(validator.errors) - 10} ошибок")

    results = aggregator.get_results()
    print("\nАгрегация по категориям")
    print(f"Всего транзакций: {results['total_transactions']}")
    print(f"Общая сумма: {results['total_amount']:.2f}")
    print("\nПо категориям:")
    for category, amount in sorted(results['summary_by_category'].items()):
        print(f"  {category}: {amount:.2f}")


def main() -> None:
    """Главная функция приложения."""
    setup_logging()
    logger = logging.getLogger(__name__)

    if len(sys.argv) != 2:
        if len(sys.argv) == 1:
            print("Папка с данными не указана. Используем 'data'")
            sys.argv.append("data")
        else:
            print("Использование: python main.py <директория>")
            print("Пример: python main.py data/")
            sys.exit(1)

    data_dir = Path(sys.argv[1])

    if not data_dir.exists():
        logger.error(f"Директория не найдена: {data_dir}")
        print(f"Ошибка: директория '{data_dir}' не существует")
        sys.exit(1)

    if not data_dir.is_dir():
        logger.error(f"Путь не является директорией: {data_dir}")
        print(f"Ошибка: '{data_dir}' не является директорией")
        sys.exit(1)

    try:
        registry = setup_registry()
        logger.info("Реестр читателей успешно инициализирован")
    except Exception as e:
        logger.error(f"Не удалось инициализировать реестр: {e}")
        sys.exit(1)

    validator = Validator()
    aggregator = Aggregator(strict_duplicate_check=False)

    files = scan_directory(data_dir)
    logger.info(f"Найдено {len(files)} файлов для обработки")

    if not files:
        logger.warning(f"В {data_dir} нет CSV или JSON файлов")
        print(f"Внимание: в '{data_dir}' нет файлов .csv или .json")
        sys.exit(0)

    total_records = 0
    total_valid = 0

    for file_path in files:
        logger.info(f"Обработка файла: {file_path.name}")
        records, valid = process_file(file_path, registry, validator)
        total_records += records
        total_valid += valid

    for transaction in validator.valid_transactions:
        try:
            aggregator.add_transaction(transaction)
        except DuplicateIdError as e:
            logger.warning(f"Дубликат ID: {e}")

    output_path = Path("result.json")
    if save_results_transactionally(aggregator, output_path):
        print(f"\nРезультаты сохранены в {output_path}")
    else:
        print("\nКритическая ошибка: не удалось сохранить результаты")
        logger.error("Не удалось сохранить результаты")
        sys.exit(1)

    print_report(validator, aggregator, len(files))

    logger.info(
        f"Обработка завершена. Валидных: {total_valid}, "
        f"Ошибок: {len(validator.errors)}"
    )
    if aggregator.get_duplicate_count() > 0:
        logger.warning(
            f"Обнаружено дубликатов ID: {aggregator.get_duplicate_count()}"
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
