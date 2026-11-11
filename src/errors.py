
class CatalogError(Exception):
    """
    Базовая ошибка пакета

    Хранит код ошибки и сообщение
    """
    def __init__(self, error_code, message):
        self.error_code = error_code
        super().__init__(message)


class InvalidEssence(CatalogError):
    """Неверная сущность"""


class DuplicateID(CatalogError):
    """Дубликат ID"""


class ObjectNotFound(CatalogError):
    """Объект не найден"""


class UnsupportedFormatVersion(CatalogError):
    """Неподдерживаемая версия формата"""

class DamagedFile(CatalogError):
    """Повреждённый файл"""
