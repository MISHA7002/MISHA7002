"""Команды /start и /help."""

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from keyboards.reply import main_menu

router = Router(name="start")

WELCOME_TEXT = (
    "👋 Добро пожаловать в DIGIT Bot.\n\n"
    "Здесь ты можешь найти AI и digital-инструменты под конкретную задачу."
)

HELP_TEXT = (
    "<b>DIGIT Bot — каталог AI и digital-инструментов</b>\n\n"
    "Команды:\n"
    "/start — главное меню\n"
    "/tools — поиск инструмента по категориям\n"
    "/new — новинки каталога\n"
    "/favorites — ваше избранное\n"
    "/help — эта справка\n\n"
    "Выберите категорию, листайте карточки кнопкой «➡️ Следующий» "
    "и сохраняйте понравившееся кнопкой «⭐ В избранное».\n\n"
    "<i>Избранное хранится временно и очищается при перезапуске бота.</i>"
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME_TEXT, reply_markup=main_menu())


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=main_menu())
