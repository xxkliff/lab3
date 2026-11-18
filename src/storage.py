import json
from collections.abc import Iterable
from dataclasses import asdict, fields
from pathlib import Path
from typing import Any

from src.constants import FORMAT_VERSION
from src.errors import CatalogError, DamagedFile, UnsupportedFormatVersion
from src.models import MediaItem


def save_items(path: Path, items: Iterable[MediaItem]) -> None:
    """
    записывает объекты в JSON файл

    :param path: путь к файлу
    :param items: объекты для записи, порядок сохраняется
    :raises OSError: нет директории или прав на запись
    """
    document = {
        "format_version": FORMAT_VERSION,
        "items": [asdict(item) for item in items],
    }

    with open(path, "w", encoding="utf-8") as file:
        json.dump(document, file, ensure_ascii=False, indent=4)


def _check_document(document: Any) -> list[Any]:
    """
    Проверяет документ и версию формата

    :param document: содержимое файла после json.load
    :return: список записей из items
    :raises UnsupportedFormatVersion: версия не совпадает с FORMAT_VERSION
    :raises DamagedFile: корень не словарь, нет нужных ключей или items не список
    """
    if not isinstance(document, dict):
        raise DamagedFile(error_code="invalid_document", message="Корень документа должен быть JSON объектом")

    if "format_version" not in document:
        raise DamagedFile(error_code="missing_key", message="В документе нет ключа format_version")

    version = document["format_version"]
    if isinstance(version, bool) or not isinstance(version, int) or version != FORMAT_VERSION:
        raise UnsupportedFormatVersion(error_code="unsupported_version",
                                       message=f"Неподдерживаемая версия формата: {version}")

    if "items" not in document:
        raise DamagedFile(error_code="missing_key", message="В документе нет ключа items")

    if not isinstance(document["items"], list):
        raise DamagedFile(error_code="invalid_items", message="items должен быть списком")

    return document["items"]


def _build_item(record: Any, number: int) -> MediaItem:
    """
    Создаёт MediaItem из одной записи документа

    список полей берётся из MediaItem, лишние ключи игнорируются

    :param record: запись из items
    :param number: номер записи, начиная с 1
    :return: объект MediaItem
    :raises DamagedFile: запись не словарь
    """
    if not isinstance(record, dict):
        raise DamagedFile(error_code="invalid_record", message=f"Запись {number} должна быть JSON объектом")

    try:
        values = {field.name: record[field.name] for field in fields(MediaItem)}
    except KeyError as e:
        raise DamagedFile(error_code="missing_key", message=f"Запись {number}: нет поля {e.args[0]}") from e

    try:
        return MediaItem(**values)
    except CatalogError as e:
        raise DamagedFile(error_code="invalid_record", message=f"Запись {number}: {e}") from e


def load_items(path: Path) -> dict[str, MediaItem]:
    """
    Читает JSON файл и собирает из него новый словарь id MediaItem

    :param path: путь к файлу
    :return: словарь объектов
    :raises DamagedFile: файл не JSON, не UTF-8, неверная структура, невалидная запись или повтор id
    :raises UnsupportedFormatVersion: версия формата не поддерживается
    :raises OSError: файл не найден или нет прав на чтение
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            document = json.load(file)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise DamagedFile(error_code="json_decode_error", message=f"Файл {path} не читается как JSON") from e

    records = _check_document(document)
    items: dict[str, MediaItem] = {}

    for number, record in enumerate(records, start=1):
        item = _build_item(record, number)

        if item.id in items:
            raise DamagedFile(error_code="duplicate_id", message=f"Запись {number}: id {item.id} уже есть в файле")

        items[item.id] = item

    return items
