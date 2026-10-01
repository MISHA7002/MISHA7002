"""Точка входа DIGIT Bot. Запуск: python bot.py"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import load_config
from handlers import get_routers
from services.favorites import FavoritesStorage

# Команды, которые Telegram покажет в меню «/» рядом с полем ввода
BOT_COMMANDS = [
    BotCommand(command="start", description="Главное меню"),
    BotCommand(command="tools", description="Найти инструмент"),
    BotCommand(command="new", description="Новинки"),
    BotCommand(command="favorites", description="Избранное"),
    BotCommand(command="help", description="Справка"),
]


def create_dispatcher(favorites: FavoritesStorage | None = None) -> Dispatcher:
    """Создаёт Dispatcher с роутерами и единым хранилищем избранного.

    Объект, переданный в Dispatcher(favorites=...), aiogram автоматически
    подставляет в любой хендлер с параметром `favorites`. Так все хендлеры
    и сервисы работают с одним и тем же экземпляром хранилища.
    """
    dp = Dispatcher(favorites=favorites if favorites is not None else FavoritesStorage())
    dp.include_routers(*get_routers())
    return dp


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    config = load_config()

    # HTML — режим разметки по умолчанию для всех сообщений
    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = create_dispatcher()

    await bot.set_my_commands(BOT_COMMANDS)
    # Сбрасываем накопившиеся апдейты, чтобы бот не отвечал на старые нажатия
    await bot.delete_webhook(drop_pending_updates=True)

    # Избранное хранится в памяти именно этого процесса. Если запустить второй
    # экземпляр бота с тем же токеном, Telegram будет раздавать апдейты то одному,
    # то другому процессу, и избранное будет «теряться» (в логах — Conflict).
    logging.info("DIGIT Bot запущен (polling). Избранное хранится в памяти процесса")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")
