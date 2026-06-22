from abc import ABC, abstractmethod


class BaseVideoParser(ABC):
    """Абстрактный базовый класс для всех поисковых плагинов площадок."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Возвращает название площадки (например, 'Rutube', 'YouTube')."""
        pass

    @abstractmethod
    async def search(self, query: str) -> list[dict]:
        """Выполняет поиск и возвращает унифицированный список словарей.

        Каждый словарь ДОЛЖЕН содержать ключи:
        - id: str
        - title: str
        - url: str
        - image: str
        - author: str
        - type: str ('video' или 'playlist')
        - source: str (имя площадки)
        - videos_count: int or None (для плейлистов)
        """
        pass
