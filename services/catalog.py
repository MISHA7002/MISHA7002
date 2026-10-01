"""Работа с каталогом инструментов.

Данные загружаются один раз из data/tools.json при импорте модуля.
Позже этот модуль можно заменить на работу с базой данных,
не меняя хендлеры.
"""

import json
from dataclasses import dataclass, field

from data import TOOLS_FILE


@dataclass(frozen=True)
class Tool:
    """Карточка инструмента."""

    id: str
    name: str
    description: str
    category: str
    price: str
    url: str
    tags: list[str] = field(default_factory=list)
    is_new: bool = False


def _load_tools() -> list[Tool]:
    with TOOLS_FILE.open(encoding="utf-8") as f:
        raw = json.load(f)
    return [Tool(**item) for item in raw]


# Все инструменты в порядке из JSON-файла
TOOLS: list[Tool] = _load_tools()
# Быстрый доступ по id
TOOLS_BY_ID: dict[str, Tool] = {tool.id: tool for tool in TOOLS}


def get_tool(tool_id: str) -> Tool | None:
    return TOOLS_BY_ID.get(tool_id)


def get_by_category(category: str) -> list[Tool]:
    return [tool for tool in TOOLS if tool.category == category]


def get_new_tools() -> list[Tool]:
    return [tool for tool in TOOLS if tool.is_new]
