# Лабораторная работа 3. Каталог объектов

Козинов Степан Андреевич, М8О-102БВ-26

Вариант: медиатека

## Возможности

- **`MediaItem`** - объект медиатеки, все поля проверяются при создании
- **`MediaCatalog`** - каталог объектов: добавление, получение, удаление, поиск по категории и названию
- сохранение каталога в JSON и атомарная загрузка из JSON

## Установка

Нужен Python 3.12 или новее и [uv](https://github.com/astral-sh/uv)

```bash
uv sync
```

## Тесты и проверки

```bash
uv run pytest
uv run pytest --cov=src
uv run ruff check .
uv run mypy src tests
```

65 тестов, покрытие `src` 95%

## Использование

```python
from pathlib import Path

from src.catalog import MediaCatalog
from src.models import MediaItem

catalog = MediaCatalog()
catalog.add(MediaItem("m-1", "test", "film", 2014, "test", 120))
catalog.add(MediaItem("m-2", "test2", "album", 2020, "test2", 40))

catalog.get("m-1")                  # объект с id m-1
catalog.find_by_name("TEST")        # [m-1, m-2]
catalog.find_by_category("album")   # [m-2]
"m-2" in catalog                    # True
len(catalog)                        # 2

catalog.save(Path("catalog.json"))
catalog.remove("m-1")
catalog.load(Path("catalog.json"))  # каталог снова из двух объектов
```

### Объект медиатеки

```text
id:           непустая строка
title:        непустая строка
category:     film | album | podcast | audiobook
year:         целое число от 1888 до текущего года
creator:      автор или исполнитель, непустая строка
duration_min: длительность в минутах, целое число больше 0
```

### Формат файла

```json
{
    "format_version": 1,
    "items": [
        {"id": "m-1", "title": "test", "category": "film", "year": 2014, "creator": "test", "duration_min": 120}
    ]
}
```

## Структура проекта

```text
src/
├── __init__.py
├── main.py          # CLI не требуется
├── models.py        # MediaItem и проверка полей
├── catalog.py       # MediaCatalog
├── storage.py       # сохранение и загрузка JSON
├── constants.py     # категории, минимальный год, версия формата
└── errors.py        # CatalogError и его наследники
tests/
├── test_models.py
├── test_catalog.py
└── test_storage.py
```

**Загрузка** выполняется по следующим шагам:

1. файл читается в UTF-8 через `json.load`.
2. корень должен быть объектом, `format_version` равен 1, `items` - список.
3. из каждой записи создаётся `MediaItem` и кладётся в новый словарь, повтор id считается ошибкой.
4. только если весь файл прошёл проверки, новый словарь заменяет текущий.

При любой ошибке на шагах 1-3 текущий каталог не меняется.

## Принятые решения

- объект неизменяемый (`frozen`), поэтому после добавления в каталог его поля нельзя испортить
- `find_by_name` ищет подстроку без учёта регистра, `find_by_category` - точное совпадение
- категория зависит от регистра: `Film` считается ошибкой
- `__contains__` принимает только id, объект `MediaItem` даёт `False`
- `remove` возвращает удалённый объект
- поиск возвращает новый список, внутренний словарь наружу не отдаётся
- `format_version` только целое 1: `"1"`, `1.0` и `true` не принимаются
- лишние ключи в записях JSON игнорируются
- отсутствующий файл не считается повреждённым, `load` пробрасывает `FileNotFoundError`
