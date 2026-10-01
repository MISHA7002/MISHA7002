"""Пакет с данными каталога (tools.json) и описанием категорий."""

from pathlib import Path

# Путь к JSON-файлу с инструментами
TOOLS_FILE = Path(__file__).parent / "tools.json"

# Категории каталога: ключ (используется в callback_data и в tools.json) -> подпись кнопки
CATEGORIES: dict[str, str] = {
    "text": "📝 Текст",
    "image": "🖼 Изображения",
    "video": "🎥 Видео",
    "voice": "🎙 Голос",
    "youtube": "🎬 YouTube",
    "code": "💻 Код",
    "service": "🛠 Сервисы",
    "telegram": "📱 Telegram",
}

# Какие категории показывать в разделе «🤖 Найти AI»
AI_CATEGORIES = ["text", "image", "video", "voice", "youtube", "code"]

# Какие категории показывать в разделе «🎬 Создать контент»
CONTENT_CATEGORIES = ["text", "image", "video", "voice", "youtube"]
