"""Временное хранилище избранного.

Хранится в памяти процесса: {telegram user_id: [tool_id, ...]}.
После перезапуска бота избранное очищается — для первой версии этого достаточно.
Позже можно заменить на SQLite/PostgreSQL/Redis с тем же интерфейсом.
"""

from services.catalog import Tool, get_tool

_favorites: dict[int, list[str]] = {}


def is_favorite(user_id: int, tool_id: str) -> bool:
    return tool_id in _favorites.get(user_id, [])


def add_favorite(user_id: int, tool_id: str) -> bool:
    """Добавляет инструмент. Возвращает False, если он уже был в избранном."""
    items = _favorites.setdefault(user_id, [])
    if tool_id in items:
        return False
    items.append(tool_id)
    return True


def remove_favorite(user_id: int, tool_id: str) -> bool:
    """Удаляет инструмент. Возвращает False, если его не было в избранном."""
    items = _favorites.get(user_id, [])
    if tool_id not in items:
        return False
    items.remove(tool_id)
    return True


def get_favorites(user_id: int) -> list[Tool]:
    """Список инструментов пользователя в порядке добавления."""
    tools = (get_tool(tool_id) for tool_id in _favorites.get(user_id, []))
    return [tool for tool in tools if tool is not None]
