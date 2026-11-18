from collections.abc import Iterator

from src.errors import DuplicateID, InvalidEssence, ObjectNotFound
from src.models import MediaItem


class MediaCatalog:
    """
    Каталог объектов медиатеки
    """

    def __init__(self) -> None:
        self._items: dict[str, MediaItem] = {}

    def add(self, item: MediaItem) -> None:
        """
        Добавляет объект в каталог

        :param item: объект медиатеки
        :raises InvalidEssence: передан не MediaItem
        :raises DuplicateID: объект с таким id уже есть в каталоге
        """
        if not isinstance(item, MediaItem):
            raise InvalidEssence(error_code="invalid_type",
                                 message=f"В каталог можно добавить только MediaItem, получен {type(item).__name__}")
        if item.id in self._items:
            raise DuplicateID(error_code="duplicate_id", message=f"Объект с id {item.id} уже есть в каталоге")

        self._items[item.id] = item

    def get(self, item_id: str) -> MediaItem:
        """
        Возвращает объект по id

        :param item_id: id объекта
        :return: найденный объект
        :raises ObjectNotFound: объекта с таким id нет в каталоге
        """
        if item_id not in self:
            raise ObjectNotFound(error_code="object_not_found", message=f"Объект с id {item_id} не найден")

        return self._items[item_id]

    def remove(self, item_id: str) -> MediaItem:
        """
        Удаляет объект по id

        :param item_id: id объекта
        :return: удалённый объект
        :raises ObjectNotFound: объекта с таким id нет в каталоге
        """
        if item_id not in self:
            raise ObjectNotFound(error_code="object_not_found", message=f"Объект с id {item_id} не найден")

        return self._items.pop(item_id)

    def find_by_name(self, name: str) -> list[MediaItem]:
        """
        Ищет объекты, в названии которых есть подстрока name

        :param name: подстрока для поиска
        :return: новый список найденных объектов в порядке добавления
        """
        query = name.casefold()
        return [item for item in self._items.values() if query in item.title.casefold()]

    def find_by_category(self, category: str) -> list[MediaItem]:
        """
        Ищет объекты с точно такой же категорией

        :param category: категория из CATEGORIES
        :return: новый список найденных объектов в порядке добавления
        """
        return [item for item in self._items.values() if item.category == category]

    def __len__(self) -> int:
        """
        :return: количество объектов в каталоге
        """
        return len(self._items)

    def __contains__(self, item_id: object) -> bool:
        """
        Проверяет, есть ли в каталоге объект с таким id

        принимает именно id, а не объект MediaItem

        :param item_id: id объекта
        :return: True, если объект есть, иначе False
        """
        return isinstance(item_id, str) and item_id in self._items

    def __iter__(self) -> Iterator[MediaItem]:
        """
        Перебирает объекты в порядке добавления

        :return: итератор по объектам
        """
        return iter(list(self._items.values()))
