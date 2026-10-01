"""Формирование карточек инструментов (текст + клавиатура)."""

from html import escape

from aiogram.types import InlineKeyboardMarkup

from data import CATEGORIES
from keyboards.inline import SOURCE_FAVORITES, SOURCE_NEW, tool_card
from services.catalog import Tool, get_by_category, get_new_tools
from services.favorites import get_favorites, is_favorite


def get_source_tools(source: str, user_id: int) -> list[Tool]:
    """Возвращает список инструментов для источника (категория / избранное / новинки)."""
    if source == SOURCE_FAVORITES:
        return get_favorites(user_id)
    if source == SOURCE_NEW:
        return get_new_tools()
    return get_by_category(source)


def format_tool(tool: Tool, position: int, total: int) -> str:
    """Текст карточки в HTML-разметке Telegram."""
    tags = " ".join(f"#{escape(tag.replace(' ', '_'))}" for tag in tool.tags)
    new_mark = " 🔥" if tool.is_new else ""
    return (
        f"<b>{escape(tool.name)}</b>{new_mark}\n\n"
        f"{escape(tool.description)}\n\n"
        f"📂 Категория: {CATEGORIES.get(tool.category, tool.category)}\n"
        f"💰 Цена: {escape(tool.price)}\n"
        f"🏷 {tags}\n\n"
        f"<i>{position} из {total}</i>"
    )


def build_card(
    source: str, index: int, user_id: int, menu: str = "ai"
) -> tuple[str, InlineKeyboardMarkup] | None:
    """Собирает карточку для позиции index в источнике.

    Индекс берётся по модулю длины списка, поэтому «➡️ Следующий»
    после последнего инструмента возвращает к первому.
    Возвращает None, если список пуст.
    """
    tools = get_source_tools(source, user_id)
    if not tools:
        return None
    index %= len(tools)
    tool = tools[index]
    text = format_tool(tool, index + 1, len(tools))
    markup = tool_card(
        url=tool.url,
        source=source,
        index=index,
        in_favorites=is_favorite(user_id, tool.id),
        menu=menu,
        has_next=len(tools) > 1,
    )
    return text, markup
