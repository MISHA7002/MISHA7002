"""Точка входа DIGIT Bot. Запуск: python bot.py"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import load_config
from handlers import get_routers

# Команды, которые Telegram покажет в меню «/» рядом с полем ввода
BOT_COMMANDS = [
    BotCommand(command="start", description="Главное меню"),
    BotCommand(command="tools", description="Найти инструмент"),
    BotCommand(command="new", description="Новинки"),
    BotCommand(command="favorites", description="Избранное"),
    BotCommand(command="help", description="Справка"),
]


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    config = load_config()

    # HTML — режим разметки по умолчанию для всех сообщений
    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_routers(*get_routers())

    await bot.set_my_commands(BOT_COMMANDS)
    # Сбрасываем накопившиеся апдейты, чтобы бот не отвечал на старые нажатия
    await bot.delete_webhook(drop_pending_updates=True)

    logging.info("DIGIT Bot запущен (polling)")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")
