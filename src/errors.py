class CatalogError(Exception):
    """
    Базовая ошибка пакета

    Хранит код ошибки и сообщение
    """
    def __init__(self, error_code: str, message: str) -> None:
        """
        :param error_code: код ошибки для тестов и обработки
        :param message: сообщение для пользователя
        """
        super().__init__(message)
        self.error_code = error_code
        self.message = message


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
