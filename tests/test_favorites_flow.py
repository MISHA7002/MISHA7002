"""Сквозной тест избранного: add -> favorites -> remove -> favorites.

Апдейты подаются прямо в Dispatcher, запросы к Telegram перехватываются
фейковым ботом — сеть и настоящий BOT_TOKEN не нужны.
"""

import datetime

import pytest
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.methods import EditMessageText, SendMessage
from aiogram.types import CallbackQuery, Chat, Message, Update, User

from bot import create_dispatcher
from handlers import get_routers

USER_ID = 42
OTHER_USER_ID = 777


@pytest.fixture(autouse=True)
def detach_routers():
    """Роутеры — объекты уровня модуля и подключаются только к одному Dispatcher.

    После каждого теста отвязываем их, чтобы следующий тест мог создать
    свой Dispatcher (в боевом коде Dispatcher создаётся один раз).
    """
    yield
    for router in get_routers():
        router._parent_router = None


class FakeBot(Bot):
    """Бот, который не ходит в сеть, а запоминает вызванные методы API."""

    def __init__(self) -> None:
        # Фиктивный токен в правильном формате, к Telegram не отправляется
        super().__init__("123456:TEST", default=DefaultBotProperties(parse_mode="HTML"))
        self.calls: list = []

    async def __call__(self, method, request_timeout=None):
        self.calls.append(method)
        return True


def _message(user_id: int, text: str) -> Message:
    return Message(
        message_id=1,
        date=datetime.datetime.now(),
        chat=Chat(id=user_id, type="private"),
        from_user=User(id=user_id, is_bot=False, first_name="Test"),
        text=text,
    )


def _callback(user_id: int, data: str) -> CallbackQuery:
    return CallbackQuery(
        id="1",
        from_user=User(id=user_id, is_bot=False, first_name="Test"),
        chat_instance="test",
        data=data,
        message=_message(user_id, "card"),
    )


async def _feed(dp: Dispatcher, bot: FakeBot, **update) -> list:
    bot.calls.clear()
    await dp.feed_update(bot, Update(update_id=1, **update))
    return list(bot.calls)


def _texts(calls: list) -> list[str]:
    return [c.text for c in calls if isinstance(c, (SendMessage, EditMessageText))]


def _buttons(calls: list) -> list[str]:
    result = []
    for c in calls:
        markup = getattr(c, "reply_markup", None)
        for row in getattr(markup, "inline_keyboard", None) or []:
            result.extend(button.text for button in row)
    return result


@pytest.mark.asyncio
async def test_add_favorites_remove_favorites():
    dp = create_dispatcher()
    bot = FakeBot()

    # 1. Открываем категорию «Код» — карточка без избранного
    calls = await _feed(dp, bot, callback_query=_callback(USER_ID, "cat:code:ai"))
    assert "⭐ В избранное" in _buttons(calls)

    # 2. add: добавляем первый инструмент категории
    calls = await _feed(dp, bot, callback_query=_callback(USER_ID, "tool:fav:code:0:ai"))
    assert "💔 Убрать из избранного" in _buttons(calls)
    assert "⭐ В избранное" not in _buttons(calls)

    # 3. favorites: /favorites и кнопка меню видят добавленный инструмент
    for text in ("/favorites", "⭐ Избранное"):
        calls = await _feed(dp, bot, message=_message(USER_ID, text))
        joined = "\n".join(_texts(calls))
        assert "GitHub Copilot" in joined, joined
        assert "пока ничего нет" not in joined
        assert "💔 Убрать из избранного" in _buttons(calls)

    # Чужое избранное не смешивается с нашим
    calls = await _feed(dp, bot, message=_message(OTHER_USER_ID, "/favorites"))
    assert "пока ничего нет" in "\n".join(_texts(calls))

    # Повторное открытие той же карточки в каталоге показывает актуальное состояние
    calls = await _feed(dp, bot, callback_query=_callback(USER_ID, "cat:code:ai"))
    assert "💔 Убрать из избранного" in _buttons(calls)

    # 4. remove: убираем из карточки каталога
    calls = await _feed(dp, bot, callback_query=_callback(USER_ID, "tool:fav:code:0:ai"))
    assert "⭐ В избранное" in _buttons(calls)

    # 5. favorites: снова пусто
    calls = await _feed(dp, bot, message=_message(USER_ID, "/favorites"))
    assert "пока ничего нет" in "\n".join(_texts(calls))


@pytest.mark.asyncio
async def test_handlers_share_one_injected_storage():
    from services.favorites import FavoritesStorage

    storage = FavoritesStorage()
    dp = create_dispatcher(storage)
    bot = FakeBot()

    # Добавление из карточки попадает в тот же объект, что передан в Dispatcher
    await _feed(dp, bot, callback_query=_callback(USER_ID, "tool:fav:code:0:ai"))
    assert [tool.id for tool in storage.list(USER_ID)] == ["github-copilot"]

    # Изменение хранилища напрямую сразу видно в /favorites
    storage.add(USER_ID, "canva")
    calls = await _feed(dp, bot, message=_message(USER_ID, "/favorites"))
    assert "Canva" in "\n".join(_texts(calls))

    # Удаление из самой карточки «Избранного»: показывается следующая, затем пусто
    calls = await _feed(dp, bot, callback_query=_callback(USER_ID, "tool:fav:fav:0:ai"))
    assert "Canva" in "\n".join(_texts(calls))
    calls = await _feed(dp, bot, callback_query=_callback(USER_ID, "tool:fav:fav:0:ai"))
    assert "пока ничего нет" in "\n".join(_texts(calls))
    assert storage.list(USER_ID) == []
