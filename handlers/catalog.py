"""Каталог: меню категорий, списки инструментов, листание карточек."""

from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from data import AI_CATEGORIES, CATEGORIES, CONTENT_CATEGORIES
from keyboards.inline import SOURCE_NEW, CategoryCallback, MenuCallback, ToolCallback, categories_menu
from keyboards.reply import BTN_CONTENT, BTN_FIND_AI, BTN_NEW, BTN_SERVICE, BTN_TELEGRAM
from services.cards import build_card
from services.favorites import FavoritesStorage

router = Router(name="catalog")

AI_MENU_TEXT = "🤖 <b>Найти AI</b>\n\nВыберите категорию:"
CONTENT_MENU_TEXT = "🎬 <b>Создать контент</b>\n\nЧто будем создавать?"

# Меню категорий: ключ -> (текст, список категорий)
MENUS = {
    "ai": (AI_MENU_TEXT, AI_CATEGORIES),
    "content": (CONTENT_MENU_TEXT, CONTENT_CATEGORIES),
}


async def send_card(message: Message, source: str, favorites: FavoritesStorage, empty_text: str) -> None:
    """Отправляет новое сообщение с первой карточкой источника."""
    card = build_card(source, 0, message.from_user.id, favorites)
    if card is None:
        await message.answer(empty_text)
        return
    text, markup = card
    await message.answer(text, reply_markup=markup, disable_web_page_preview=True)


async def edit_card(
    callback: CallbackQuery,
    source: str,
    index: int,
    menu: str,
    favorites: FavoritesStorage,
    empty_text: str,
) -> None:
    """Перерисовывает текущее сообщение с карточкой."""
    card = build_card(source, index, callback.from_user.id, favorites, menu)
    # suppress: Telegram ругается, если текст и клавиатура не изменились
    with suppress(TelegramBadRequest):
        if card is None:
            await callback.message.edit_text(empty_text)
        else:
            text, markup = card
            await callback.message.edit_text(text, reply_markup=markup, disable_web_page_preview=True)


# ---------- Главное меню и команды ----------


@router.message(Command("tools"))
@router.message(F.text == BTN_FIND_AI)
async def show_ai_menu(message: Message) -> None:
    await message.answer(AI_MENU_TEXT, reply_markup=categories_menu(AI_CATEGORIES, "ai"))


@router.message(F.text == BTN_CONTENT)
async def show_content_menu(message: Message) -> None:
    await message.answer(CONTENT_MENU_TEXT, reply_markup=categories_menu(CONTENT_CATEGORIES, "content"))


@router.message(F.text == BTN_SERVICE)
async def show_services(message: Message, favorites: FavoritesStorage) -> None:
    await send_card(message, "service", favorites, "Сервисов пока нет.")


@router.message(F.text == BTN_TELEGRAM)
async def show_telegram(message: Message, favorites: FavoritesStorage) -> None:
    await send_card(message, "telegram", favorites, "Telegram-инструментов пока нет.")


@router.message(Command("new"))
@router.message(F.text == BTN_NEW)
async def show_new(message: Message, favorites: FavoritesStorage) -> None:
    await message.answer("🔥 <b>Новинки каталога</b>")
    await send_card(message, SOURCE_NEW, favorites, "Новинок пока нет.")


# ---------- Inline-навигация ----------


@router.callback_query(MenuCallback.filter())
async def on_menu(callback: CallbackQuery, callback_data: MenuCallback) -> None:
    """Кнопка «⬅️ Назад»: возврат в меню категорий или закрытие меню."""
    menu = MENUS.get(callback_data.action)
    with suppress(TelegramBadRequest):
        if menu is None:
            await callback.message.edit_text("Выберите раздел в меню ниже 👇")
        else:
            text, categories = menu
            await callback.message.edit_text(text, reply_markup=categories_menu(categories, callback_data.action))
    await callback.answer()


@router.callback_query(CategoryCallback.filter())
async def on_category(callback: CallbackQuery, callback_data: CategoryCallback, favorites: FavoritesStorage) -> None:
    """Выбор категории — показываем первую карточку."""
    title = CATEGORIES.get(callback_data.category, callback_data.category)
    await edit_card(
        callback, callback_data.category, 0, callback_data.menu, favorites, f"В категории {title} пока пусто."
    )
    await callback.answer()


@router.callback_query(ToolCallback.filter(F.action.in_({"show", "next"})))
async def on_next(callback: CallbackQuery, callback_data: ToolCallback, favorites: FavoritesStorage) -> None:
    """Кнопка «➡️ Следующий»."""
    await edit_card(callback, callback_data.source, callback_data.index, callback_data.menu, favorites, "Список пуст.")
    await callback.answer()
