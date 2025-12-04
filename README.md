# Secret Santa Telegram Bot

A Telegram bot for organizing Secret Santa gift exchanges with persistent storage using Supabase.

## Features

- Create multiple Secret Santa games
- Participants can join games
- Random assignment of gift givers and receivers
- Private message notifications to each participant
- Persistent storage in Supabase database

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token provided by BotFather

### 3. Configure Environment Variables

Edit the `.env` file and replace `YOUR_TELEGRAM_BOT_TOKEN_HERE` with your actual bot token:

```
TELEGRAM_BOT_TOKEN=your_actual_token_here
```

The Supabase credentials are already configured.

### 4. Run the Bot

```bash
python bot.py
```

## Usage

### Commands

- `/start` or `/help` - Show available commands
- `/new_game` - Create a new Secret Santa game in the current chat
- `/join` - Join the current game
- `/list` - Show all participants in the current game
- `/start_game` - Start the game and distribute assignments (minimum 2 participants required)

### Example Workflow

1. **Create a game**: Send `/new_game` in your Telegram group or chat
2. **Join the game**: Each participant sends `/join`
3. **Check participants**: Send `/list` to see who has joined
4. **Start the game**: When everyone has joined, send `/start_game`
5. **Receive assignments**: Each participant will receive a private message from the bot with their Secret Santa assignment

## Important Notes

- The bot needs to be able to send private messages to participants. Users must start a conversation with the bot first (by sending `/start` to the bot directly) before they can receive private messages.
- Each chat can have one active game at a time
- Minimum 2 participants required to start a game
- Assignments are random and ensure each person gives to exactly one other person

## Database Schema

The bot uses three tables in Supabase:

- `games` - Stores game sessions
- `participants` - Stores participants for each game
- `assignments` - Stores who gives to whom

All data is persisted and can be used for future features like game history or statistics.

Есть несколько вариантов, где запустить бота:

1. Локально (быстро для тестирования)

python bot.py
Бот работает пока вы запущены. Удобно для разработки.

2. На облачном сервере (VPS)
   Популярные варианты:

DigitalOcean - $5-6/мес
Hetzner - €3-4/мес
Linode - $5/мес
Яндекс.Облако / 2cloudservers (если из РФ)
Как:

Берете сервер с Linux (Ubuntu 22.04)
Подключаетесь по SSH
Устанавливаете Python: sudo apt install python3-pip
Загружаете код: git clone ваш-репо
Устанавливаете зависимости: pip install -r requirements.txt
Запускаете в фоне с systemd или screen:

screen -S santa_bot
python bot.py

# Ctrl+A, D для выхода

3. Бесплатные платформы (для обучения)
   Railway.app - 500 часов/мес бесплатно
   Render - бесплатный tier с перезагрузками
   Replit - можно с использованием always-on (платно)
4. Для автоматизма (рекомендую)
   Добавьте в systemd, чтобы бот перезапускался автоматически при перезагрузке:

sudo nano /etc/systemd/system/santa-bot.service
Вставьте:

[Unit]
Description=Secret Santa Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/bot
ExecStart=/usr/bin/python3 /path/to/bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
Потом:

sudo systemctl enable santa-bot
sudo systemctl start santa-bot
Какой вариант выбрать?

Тестирование → локально
Боевое использование → VPS или Railway
Минимум заботы → Railway/Render (но они могут перезагружаться)
