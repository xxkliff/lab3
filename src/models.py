from dataclasses import dataclass
from datetime import datetime

from src.constants import CATEGORIES, MIN_YEAR
from src.errors import InvalidEssence


@dataclass(frozen=True, slots=True)
class MediaItem:
    """
    Один объект медиатеки

    id - непустая строка
    title - непустая строка
    category - одна из CATEGORIES
    year - год выхода, от MIN_YEAR до текущего года
    creator - автор или исполнитель, непустая строка
    duration_min - длительность в минутах, больше нуля
    """
    id: str
    title: str
    category: str
    year: int
    creator: str
    duration_min: int

    def __post_init__(self) -> None:
        """
        Проверяет поля MediaItem

        Объект неизменяемый, поэтому после создания поля всегда остаются валидными

        :raises InvalidEssence: неверный тип поля, пустая строка, неизвестная категория, год или длительность вне границ
        """
        only_str = {"id": self.id, "title": self.title, "category": self.category, "creator": self.creator}
        only_int = {"year": self.year, "duration_min": self.duration_min}

        # только str
        for key, value in only_str.items():
            if not isinstance(value, str):
                raise InvalidEssence(error_code="invalid_type",
                                     message=f"Значение {value} для {key} должно быть строковым")
            if len(value.strip()) == 0:
                raise InvalidEssence(error_code="empty_field", message=f"Поле {key} не может быть пустым")

        # только int
        for key, number in only_int.items():
            if isinstance(number, bool) or not isinstance(number, int):
                raise InvalidEssence(error_code="invalid_type",
                                     message=f"Значение {number} для {key} должно быть целым числом")

        # проверка category
        if self.category not in CATEGORIES:
            raise InvalidEssence(error_code="unsupported_category",
                                 message=f"Неподдерживаемая категория: {self.category}")

        # проверка year
        if not MIN_YEAR <= self.year <= datetime.now().astimezone().year:
            raise InvalidEssence(error_code="invalid_year",
                                 message=f"Год {self.year} должен быть от {MIN_YEAR} до текущего")

        # проверка duration_min
        if self.duration_min <= 0:
            raise InvalidEssence(error_code="invalid_duration",
                                 message=f"Длительность {self.duration_min} должна быть больше нуля")
