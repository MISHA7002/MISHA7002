"""Reply-клавиатура главного меню."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# Тексты кнопок вынесены в константы, чтобы хендлеры ловили их по тем же строкам
BTN_FIND_AI = "🤖 Найти AI"
BTN_CONTENT = "🎬 Создать контент"
BTN_SERVICE = "🛠 Найти сервис"
BTN_TELEGRAM = "📱 Telegram"
BTN_NEW = "🔥 Новинки"
BTN_FAVORITES = "⭐ Избранное"


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_FIND_AI), KeyboardButton(text=BTN_CONTENT)],
            [KeyboardButton(text=BTN_SERVICE), KeyboardButton(text=BTN_TELEGRAM)],
            [KeyboardButton(text=BTN_NEW), KeyboardButton(text=BTN_FAVORITES)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел",
    )
