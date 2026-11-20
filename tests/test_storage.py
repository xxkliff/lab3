import json
from pathlib import Path
from typing import Any

import pytest

from src.catalog import MediaCatalog
from src.errors import CatalogError, DamagedFile, UnsupportedFormatVersion
from src.models import MediaItem


def _record(item_id: str, title: str = "test") -> dict[str, Any]:
    """Создаёт запись документа для тестов"""
    return {"id": item_id, "title": title, "category": "film", "year": 2014, "creator": "test", "duration_min": 120}


def _write(path: Path, document: Any) -> None:
    """Записывает документ в JSON файл"""
    path.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")


def _catalog() -> MediaCatalog:
    """Создаёт каталог из двух объектов"""
    catalog = MediaCatalog()
    catalog.add(MediaItem("old-1", "old", "album", 2000, "test", 40))
    catalog.add(MediaItem("old-2", "old2", "podcast", 2010, "test2", 60))
    return catalog


def test_save_document(tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"
    _catalog().save(path)

    document = json.loads(path.read_text(encoding="utf-8"))

    assert document["format_version"] == 1
    assert document["items"][0] == {"id": "old-1", "title": "old", "category": "album", "year": 2000,
                                    "creator": "test", "duration_min": 40}
    assert len(document["items"]) == 2


@pytest.mark.parametrize(
    ("document", "error_class", "error_code"),
    [
        ([], DamagedFile, "invalid_document"),
        ({"format_version": 2, "items": []}, UnsupportedFormatVersion, "unsupported_version"),
        ({"format_version": "1", "items": []}, UnsupportedFormatVersion, "unsupported_version"),
        ({"format_version": 1}, DamagedFile, "missing_key"),
        ({"format_version": 1, "items": {}}, DamagedFile, "invalid_items"),
        ({"format_version": 1, "items": [{"id": "m-1"}]}, DamagedFile, "missing_key"),
        ({"format_version": 1, "items": [_record("m-1"), _record("m-1")]}, DamagedFile, "duplicate_id"),
    ],
)
def test_load_invalid_document(tmp_path: Path, document: Any, error_class: type[CatalogError],
                               error_code: str) -> None:
    path = tmp_path / "catalog.json"
    _write(path, document)
    catalog = _catalog()

    with pytest.raises(error_class) as exc_info:
        catalog.load(path)

    assert exc_info.value.error_code == error_code
    assert [item.id for item in catalog] == ["old-1", "old-2"]


def test_load_not_found(tmp_path: Path) -> None:
    catalog = _catalog()

    with pytest.raises(FileNotFoundError):
        catalog.load(tmp_path / "no_exist.json")

    assert len(catalog) == 2


@pytest.mark.parametrize("content", [b"", b"{", b'{"format_version": 1, "items": [}', b"\xff\xfe\x00"])
def test_load_not_json(tmp_path: Path, content: bytes) -> None:
    path = tmp_path / "catalog.json"
    path.write_bytes(content)
    catalog = _catalog()

    with pytest.raises(DamagedFile) as exc_info:
        catalog.load(path)

    assert exc_info.value.error_code == "json_decode_error"
    assert [item.id for item in catalog] == ["old-1", "old-2"]


def test_load_partially_damaged(tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"
    broken = _record("m-4")
    del broken["title"]
    _write(path, {"format_version": 1, "items": [_record("m-1"), _record("m-2"), _record("m-3"), broken]})
    catalog = _catalog()
    before = list(catalog)

    with pytest.raises(DamagedFile) as exc_info:
        catalog.load(path)

    assert exc_info.value.error_code == "missing_key"
    assert "Запись 4" in str(exc_info.value)
    assert list(catalog) == before
    assert "m-1" not in catalog
