"""Хранилище избранного.

Один экземпляр FavoritesStorage создаётся в bot.py и передаётся во все
хендлеры через Dispatcher (dp["favorites"]), поэтому у всего приложения
одно общее хранилище. Данные лежат в памяти процесса:
{telegram user_id: [tool_id, ...]} и очищаются при перезапуске бота.

Чтобы подключить базу данных, достаточно написать класс с теми же
методами и передать его экземпляр в create_dispatcher().
"""

from services.catalog import Tool, get_tool


class FavoritesStorage:
    def __init__(self) -> None:
        self._data: dict[int, list[str]] = {}

    def is_favorite(self, user_id: int, tool_id: str) -> bool:
        return tool_id in self._data.get(user_id, [])

    def add(self, user_id: int, tool_id: str) -> bool:
        """Добавляет инструмент. Возвращает False, если он уже был в избранном."""
        items = self._data.setdefault(user_id, [])
        if tool_id in items:
            return False
        items.append(tool_id)
        return True

    def remove(self, user_id: int, tool_id: str) -> bool:
        """Удаляет инструмент. Возвращает False, если его не было в избранном."""
        items = self._data.get(user_id, [])
        if tool_id not in items:
            return False
        items.remove(tool_id)
        return True

    def toggle(self, user_id: int, tool_id: str) -> bool:
        """Переключает состояние. Возвращает True, если инструмент теперь в избранном."""
        if self.remove(user_id, tool_id):
            return False
        self.add(user_id, tool_id)
        return True

    def list(self, user_id: int) -> list[Tool]:
        """Инструменты пользователя в порядке добавления."""
        tools = (get_tool(tool_id) for tool_id in self._data.get(user_id, []))
        return [tool for tool in tools if tool is not None]
