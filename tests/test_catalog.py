from typing import Any

import pytest

from src.catalog import MediaCatalog
from src.errors import DuplicateID, InvalidEssence, ObjectNotFound
from src.models import MediaItem


def _item(item_id: str, title: str = "test", category: str = "film") -> MediaItem:
    """Создаёт валидный MediaItem для тестов"""
    return MediaItem(item_id, title, category, 2014, "test", 120)


def _catalog() -> MediaCatalog:
    """Создаёт каталог из трёх объектов"""
    catalog = MediaCatalog()
    catalog.add(_item("m-1", "test", "film"))
    catalog.add(_item("m-2", "test2", "album"))
    catalog.add(_item("m-3", "test3", "album"))
    return catalog


def test_empty_catalog() -> None:
    catalog = MediaCatalog()

    assert len(catalog) == 0
    assert not catalog
    assert list(catalog) == []
    assert catalog.find_by_name("test") == []
    assert catalog.find_by_category("film") == []


def test_add_and_get() -> None:
    catalog = MediaCatalog()
    item = _item("m-1")
    catalog.add(item)

    assert len(catalog) == 1
    assert catalog.get("m-1") is item


def test_add_duplicate() -> None:
    catalog = MediaCatalog()
    first = _item("m-1", "first")
    catalog.add(first)

    with pytest.raises(DuplicateID) as exc_info:
        catalog.add(_item("m-1", "second"))

    assert exc_info.value.error_code == "duplicate_id"
    assert len(catalog) == 1
    assert catalog.get("m-1") is first


@pytest.mark.parametrize("value", [None, "m-1", {"id": "m-1"}, 1])
def test_add_not_item(value: Any) -> None:
    catalog = MediaCatalog()

    with pytest.raises(InvalidEssence) as exc_info:
        catalog.add(value)

    assert exc_info.value.error_code == "invalid_type"
    assert len(catalog) == 0


@pytest.mark.parametrize("item_id", ["m-404", "", "M-1", 1, None, ["m-1"]])
def test_get_not_found(item_id: Any) -> None:
    catalog = _catalog()

    with pytest.raises(ObjectNotFound) as exc_info:
        catalog.get(item_id)

    assert exc_info.value.error_code == "object_not_found"


def test_remove() -> None:
    catalog = _catalog()
    removed = catalog.remove("m-2")

    assert removed.title == "test2"
    assert len(catalog) == 2
    assert "m-2" not in catalog
    assert [item.id for item in catalog] == ["m-1", "m-3"]


def test_remove_not_found() -> None:
    catalog = _catalog()

    with pytest.raises(ObjectNotFound) as exc_info:
        catalog.remove("m-404")

    assert exc_info.value.error_code == "object_not_found"
    assert len(catalog) == 3


def test_contains() -> None:
    catalog = _catalog()

    assert "m-1" in catalog
    assert "m-404" not in catalog
    assert catalog.get("m-1") not in catalog
    assert 1 not in catalog
    assert ["m-1"] not in catalog


def test_iter_order() -> None:
    catalog = _catalog()
    catalog.remove("m-1")
    catalog.add(_item("m-1"))

    assert [item.id for item in catalog] == ["m-2", "m-3", "m-1"]


def test_iter_with_remove() -> None:
    catalog = _catalog()

    for item in catalog:
        catalog.remove(item.id)

    assert len(catalog) == 0


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("test", ["m-1", "m-2", "m-3"]),
        ("TEST", ["m-1", "m-2", "m-3"]),
        ("test2", ["m-2"]),
        ("TeSt3", ["m-3"]),
        ("2", ["m-2"]),
        ("nothing", []),
    ],
)
def test_find_by_name(name: str, expected: list[str]) -> None:
    catalog = _catalog()

    assert [item.id for item in catalog.find_by_name(name)] == expected


@pytest.mark.parametrize(
    ("category", "expected"),
    [
        ("film", ["m-1"]),
        ("album", ["m-2", "m-3"]),
        ("podcast", []),
        ("Film", []),
    ],
)
def test_find_by_category(category: str, expected: list[str]) -> None:
    catalog = _catalog()

    assert [item.id for item in catalog.find_by_category(category)] == expected


def test_find_returns_new_list() -> None:
    catalog = _catalog()
    found = catalog.find_by_category("album")
    found.clear()
    found_by_name = catalog.find_by_name("2")
    found_by_name.append(_item("m-99"))

    assert len(catalog) == 3
    assert len(catalog.find_by_category("album")) == 2
    assert "m-99" not in catalog
    assert catalog.find_by_name("2") is not catalog.find_by_name("2")
