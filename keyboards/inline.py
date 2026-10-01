"""Inline-клавиатуры и фабрики callback_data."""

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data import AI_CATEGORIES, CATEGORIES

# Специальные «источники» списка, помимо категорий
SOURCE_FAVORITES = "fav"
SOURCE_NEW = "new"


class MenuCallback(CallbackData, prefix="menu"):
    """Навигация по меню: action = 'ai' | 'content' | 'close'."""

    action: str


class CategoryCallback(CallbackData, prefix="cat"):
    """Выбор категории; menu — в какое меню вернуться по кнопке «Назад»."""

    category: str
    menu: str = "ai"


class ToolCallback(CallbackData, prefix="tool"):
    """Действие с карточкой инструмента.

    action: 'show' | 'next' | 'fav'
    source: ключ категории, 'fav' (избранное) или 'new' (новинки)
    index:  позиция инструмента в списке источника
    menu:   меню, в которое ведёт кнопка «Назад»
    """

    action: str
    source: str
    index: int
    menu: str = "ai"


def categories_menu(categories: list[str] = AI_CATEGORIES, menu: str = "ai") -> InlineKeyboardMarkup:
    """Клавиатура выбора категории (по две кнопки в ряд) + «Назад»."""
    builder = InlineKeyboardBuilder()
    for key in categories:
        builder.button(text=CATEGORIES[key], callback_data=CategoryCallback(category=key, menu=menu))
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=MenuCallback(action="close").pack()))
    return builder.as_markup()


def tool_card(
    url: str,
    source: str,
    index: int,
    in_favorites: bool,
    menu: str = "ai",
    has_next: bool = True,
) -> InlineKeyboardMarkup:
    """Кнопки под карточкой инструмента."""
    fav_text = "💔 Убрать из избранного" if in_favorites else "⭐ В избранное"
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🌐 Открыть", url=url))
    builder.row(
        InlineKeyboardButton(
            text=fav_text,
            callback_data=ToolCallback(action="fav", source=source, index=index, menu=menu).pack(),
        )
    )
    nav = []
    # «Назад» возвращает в меню категорий, из которого пользователь пришёл
    nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=MenuCallback(action=menu).pack()))
    if has_next:
        nav.append(
            InlineKeyboardButton(
                text="➡️ Следующий",
                callback_data=ToolCallback(action="next", source=source, index=index + 1, menu=menu).pack(),
            )
        )
    builder.row(*nav)
    return builder.as_markup()
