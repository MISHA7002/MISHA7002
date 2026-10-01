"""Сборка всех роутеров в один список для подключения в bot.py."""

from aiogram import Router

from handlers import catalog, favorites, start


def get_routers() -> list[Router]:
    # Порядок важен: start/help первыми, затем каталог и избранное
    return [start.router, catalog.router, favorites.router]
