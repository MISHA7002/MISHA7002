"""Избранное: команда /favorites и кнопка «⭐ В избранное»."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from handlers.catalog import edit_card, send_card
from keyboards.inline import SOURCE_FAVORITES, ToolCallback
from keyboards.reply import BTN_FAVORITES
from services.cards import get_source_tools
from services.favorites import add_favorite, is_favorite, remove_favorite

router = Router(name="favorites")

EMPTY_FAVORITES = (
    "⭐ В избранном пока ничего нет.\n\n"
    "Откройте каталог (/tools) и нажмите «⭐ В избранное» на карточке инструмента."
)


@router.message(Command("favorites"))
@router.message(F.text == BTN_FAVORITES)
async def show_favorites(message: Message) -> None:
    user_id = message.from_user.id
    tools = get_source_tools(SOURCE_FAVORITES, user_id)
    if tools:
        names = "\n".join(f"• {tool.name}" for tool in tools)
        await message.answer(f"⭐ <b>Ваше избранное</b> ({len(tools)}):\n\n{names}")
    await send_card(message, SOURCE_FAVORITES, user_id, EMPTY_FAVORITES)


@router.callback_query(ToolCallback.filter(F.action == "fav"))
async def toggle_favorite(callback: CallbackQuery, callback_data: ToolCallback) -> None:
    """Добавляет инструмент в избранное или убирает его оттуда."""
    user_id = callback.from_user.id
    tools = get_source_tools(callback_data.source, user_id)
    if not tools:
        await callback.answer("Список пуст", show_alert=True)
        return

    tool = tools[callback_data.index % len(tools)]
    if is_favorite(user_id, tool.id):
        remove_favorite(user_id, tool.id)
        notice = f"Удалено из избранного: {tool.name}"
    else:
        add_favorite(user_id, tool.id)
        notice = f"⭐ Добавлено в избранное: {tool.name}"

    # Перерисовываем карточку, чтобы обновилась кнопка.
    # В разделе «Избранное» удалённая карточка исчезнет, и покажется следующая.
    await edit_card(callback, callback_data.source, callback_data.index, callback_data.menu, EMPTY_FAVORITES)
    await callback.answer(notice)
