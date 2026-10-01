# DIGIT Bot

Telegram-бот — каталог AI и digital-инструментов. Помогает найти инструмент под конкретную задачу: тексты, изображения, видео, голос, YouTube, код, сервисы и Telegram.

- Python 3.12, [aiogram 3.x](https://docs.aiogram.dev/)
- Режим работы: **long polling** (не нужен домен и HTTPS)
- Без платных API: данные хранятся в `data/tools.json`, избранное — в памяти

## Возможности

| Команда / кнопка | Что делает |
|---|---|
| `/start` | Приветствие и главное меню |
| `/tools`, «🤖 Найти AI» | Выбор категории: Текст, Изображения, Видео, Голос, YouTube, Код |
| «🎬 Создать контент» | Категории для создания контента |
| «🛠 Найти сервис» | Digital-сервисы (Canva, Notion, Gamma) |
| «📱 Telegram» | Инструменты для Telegram |
| `/new`, «🔥 Новинки» | Новые инструменты каталога |
| `/favorites`, «⭐ Избранное» | Сохранённые инструменты |
| `/help` | Краткая справка |

У каждой карточки инструмента есть кнопки **🌐 Открыть**, **⭐ В избранное**, **➡️ Следующий**, **⬅️ Назад**.

> ⚠️ Избранное хранится в памяти процесса и очищается при перезапуске бота. На всё приложение есть одно хранилище (`FavoritesStorage`): оно создаётся в `bot.py` и передаётся во все хендлеры через Dispatcher. Чтобы перейти на SQLite/PostgreSQL, напишите класс с теми же методами и передайте его в `create_dispatcher()`.

## Структура проекта

```
.
├── bot.py               # Точка входа: создание бота, подключение роутеров, polling
├── config.py            # Чтение BOT_TOKEN из окружения / .env
├── handlers/            # Обработчики команд и кнопок
│   ├── start.py         #   /start, /help
│   ├── catalog.py       #   меню, категории, /tools, /new, листание карточек
│   └── favorites.py     #   /favorites, добавление/удаление из избранного
├── keyboards/
│   ├── reply.py         # Главное меню (ReplyKeyboardMarkup)
│   └── inline.py        # Inline-клавиатуры и CallbackData
├── data/
│   ├── __init__.py      # Список категорий
│   └── tools.json       # Каталог инструментов
├── services/
│   ├── catalog.py       # Загрузка и выборка инструментов
│   ├── favorites.py     # FavoritesStorage: избранное в памяти по user_id
│   └── cards.py         # Сборка текста и кнопок карточки
├── tests/               # Тесты сценариев (без сети и без токена)
├── requirements.txt
├── requirements-dev.txt # Зависимости для тестов
├── .env.example
└── README.md
```

## 1. Получение токена

1. Откройте в Telegram [@BotFather](https://t.me/BotFather).
2. Отправьте `/newbot`, задайте имя и username бота (должен заканчиваться на `bot`).
3. BotFather пришлёт токен вида `1234567890:AAH...`. **Никому его не показывайте** и не публикуйте в репозитории.

## 2. Установка зависимостей

Нужен Python 3.12 (подойдёт и 3.10+).

```bash
git clone <url-репозитория> digit-bot
cd digit-bot

# Виртуальное окружение
python3.12 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## 3. Создание .env и BOT_TOKEN

Скопируйте пример:

```bash
cp .env.example .env             # Windows: copy .env.example .env
```

Откройте `.env` и вставьте свой токен **вместо** `your_telegram_bot_token_here`:

```env
BOT_TOKEN=1234567890:AAH_ваш_токен_от_BotFather
```

Файл `.env` уже добавлен в `.gitignore` и не попадёт в git.

Вместо `.env` можно задать переменную окружения напрямую:

```bash
export BOT_TOKEN="1234567890:AAH..."        # Linux / macOS
$env:BOT_TOKEN="1234567890:AAH..."          # Windows PowerShell
```

Если токен не задан, бот при запуске завершится с понятной ошибкой.

## 4. Запуск локально

```bash
source .venv/bin/activate
python bot.py
```

В логе появится `DIGIT Bot запущен (polling)`. Откройте бота в Telegram и отправьте `/start`. Остановить — `Ctrl+C`.

> Одновременно должен работать только один экземпляр бота с этим токеном, иначе Telegram вернёт ошибку `Conflict: terminated by other getUpdates request`.

## Тесты

Тесты подают апдейты прямо в Dispatcher и не обращаются к Telegram, поэтому настоящий токен для них не нужен.

```bash
pip install -r requirements-dev.txt
python -m pytest -v
```

Тест `tests/test_favorites_flow.py` проверяет сценарий «добавить → /favorites → убрать → /favorites».

## Частые проблемы

**Избранное «пропадает» или `/favorites` пишет, что оно пустое.** Избранное хранится в памяти одного процесса. Это происходит в двух случаях:
- бот перезапускался: после перезапуска избранное пустое;
- запущено **несколько экземпляров** бота с одним токеном, например локально и на сервере или дважды на сервере. Тогда Telegram отдаёт апдейты то одному процессу, то другому, и в логах появляется `Conflict: terminated by other getUpdates request`. Остановите лишние копии и оставьте один процесс:
  ```bash
  ps aux | grep bot.py
  ```

## 5. Как добавить инструмент

Добавьте объект в `data/tools.json`:

```json
{
  "id": "unique-id",
  "name": "Название",
  "description": "Короткое описание",
  "category": "text",
  "price": "Бесплатно",
  "url": "https://example.com",
  "tags": ["тег1", "тег2"],
  "is_new": true
}
```

- `category` — один из ключей: `text`, `image`, `video`, `voice`, `youtube`, `code`, `service`, `telegram` (список в `data/__init__.py`).
- `is_new: true` — инструмент появится в «🔥 Новинках».
- `id` должен быть уникальным: по нему хранится избранное.

После изменения перезапустите бота.

## 6. Развёртывание на облачном сервере (VPS)

Подойдёт любой VPS с Ubuntu 22.04/24.04 (Hetzner, DigitalOcean, Timeweb, Selectel и т.п.). Для polling не нужны домен, открытые порты и SSL.

### 6.1. Подготовка сервера

```bash
ssh root@IP_СЕРВЕРА

apt update && apt upgrade -y
apt install -y git python3 python3-venv python3-pip   # на Ubuntu 24.04 python3 = 3.12

# Отдельный пользователь для бота (безопаснее, чем root)
adduser --disabled-password --gecos "" digitbot
su - digitbot
```

### 6.2. Установка бота

```bash
git clone <url-репозитория> ~/digit-bot
cd ~/digit-bot
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

cp .env.example .env
nano .env                     # вставьте BOT_TOKEN, сохраните: Ctrl+O, Enter, Ctrl+X
chmod 600 .env                # токен доступен только владельцу

.venv/bin/python bot.py       # проверочный запуск, затем Ctrl+C
exit                          # вернуться в root
```

### 6.3. Автозапуск через systemd

Создайте файл `/etc/systemd/system/digit-bot.service`:

```ini
[Unit]
Description=DIGIT Telegram Bot
After=network-online.target
Wants=network-online.target

[Service]
User=digitbot
WorkingDirectory=/home/digitbot/digit-bot
EnvironmentFile=/home/digitbot/digit-bot/.env
ExecStart=/home/digitbot/digit-bot/.venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Запустите сервис:

```bash
systemctl daemon-reload
systemctl enable --now digit-bot
systemctl status digit-bot           # статус
journalctl -u digit-bot -f           # логи в реальном времени
```

### 6.4. Обновление бота

```bash
su - digitbot -c "cd ~/digit-bot && git pull && .venv/bin/pip install -r requirements.txt"
systemctl restart digit-bot
```

### Альтернатива: Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

```bash
docker build -t digit-bot .
docker run -d --name digit-bot --restart unless-stopped --env-file .env digit-bot
```

## Дальнейшее развитие

- Хранение избранного в SQLite / PostgreSQL
- Поиск по тегам и названию
- Админ-команды для добавления инструментов
- Переход на webhook при росте нагрузки
