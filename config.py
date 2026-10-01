"""Конфигурация бота.

Токен читается только из переменной окружения BOT_TOKEN
(или из файла .env в корне проекта). Хардкодить токен в коде нельзя.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

@dataclass(frozen=True)
class Config:
    bot_token: str


def load_config() -> Config:
    """Читает настройки и падает с понятной ошибкой, если токена нет.

    .env подгружается только здесь, при запуске бота, а не при импорте модуля.
    Уже заданные переменные окружения не перезаписываются. Значение токена
    нигде не логируется.
    """
    load_dotenv()
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token or token == "your_telegram_bot_token_here":
        raise RuntimeError(
            "Не задан BOT_TOKEN. Создайте файл .env по образцу .env.example "
            "или экспортируйте переменную окружения BOT_TOKEN."
        )
    return Config(bot_token=token)
