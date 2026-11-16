import dataclasses
from typing import Any

import pytest

from src.errors import CatalogError, InvalidEssence
from src.models import MediaItem


@pytest.mark.parametrize(
    ("id", "title", "category", "year", "creator", "duration_min"),
    [
        ("m-001", "test", "film", 2014, "test", 169),
        ("m-002", "test2", "album", 1969, "test2", 47),
        ("m-003", "test3", "podcast", 2008, "test3", 120),
        ("m-004", "test4", "audiobook", 2015, "test4", 1080),
        ("1", "a", "film", 1888, "b", 1),
    ],
)
def test_positive_model(id: str, title: str, category: str, year: int, creator: str, duration_min: int) -> None:
    item = MediaItem(id, title, category, year, creator, duration_min)

    assert item.id == id
    assert item.title == title
    assert item.category == category
    assert item.year == year
    assert item.creator == creator
    assert item.duration_min == duration_min


def test_model_keywords() -> None:
    item = MediaItem(id="m-001", title="test", category="film", year=2014,
                     creator="test", duration_min=169)

    assert item.title == "test"


@pytest.mark.parametrize(
    ("id", "title", "category", "year", "creator", "duration_min", "error_code"),
    [
        (1, "a", "film", 2000, "b", 10, "invalid_type"),
        (None, "a", "film", 2000, "b", 10, "invalid_type"),
        ("m-1", ["a"], "film", 2000, "b", 10, "invalid_type"),
        ("m-1", "a", "film", 2000, None, 10, "invalid_type"),
        ("m-1", "a", "film", "2000", "b", 10, "invalid_type"),
        ("m-1", "a", "film", 2000.0, "b", 10, "invalid_type"),
        ("m-1", "a", "film", True, "b", 10, "invalid_type"),
        ("m-1", "a", "film", 2000, "b", 1.5, "invalid_type"),
        ("", "a", "film", 2000, "b", 10, "empty_field"),
        ("   ", "a", "film", 2000, "b", 10, "empty_field"),
        ("m-1", "", "film", 2000, "b", 10, "empty_field"),
        ("m-1", "a", "film", 2000, " ", 10, "empty_field"),
        ("m-1", "a", "series", 2000, "b", 10, "unsupported_category"),
        ("m-1", "a", "Film", 2000, "b", 10, "unsupported_category"),
        ("m-1", "a", "film", 1887, "b", 10, "invalid_year"),
        ("m-1", "a", "film", 3000, "b", 10, "invalid_year"),
        ("m-1", "a", "film", 2000, "b", 0, "invalid_duration"),
        ("m-1", "a", "film", 2000, "b", -5, "invalid_duration"),
    ],
)
def test_negative_model(id: Any, title: Any, category: Any, year: Any, creator: Any, duration_min: Any,
                        error_code: str) -> None:
    with pytest.raises(InvalidEssence) as exc_info:
        MediaItem(id, title, category, year, creator, duration_min)

    assert exc_info.value.error_code == error_code
    assert isinstance(exc_info.value, CatalogError)


def test_model_frozen() -> None:
    item = MediaItem("m-001", "test", "film", 2014, "test", 169)

    with pytest.raises(dataclasses.FrozenInstanceError):
        item.title = "other"  # type: ignore[misc]

    assert item.title == "test"


def test_model_equal() -> None:
    first = MediaItem("m-001", "test", "film", 2014, "test", 169)
    second = MediaItem("m-001", "test", "film", 2014, "test", 169)

    assert first == second
