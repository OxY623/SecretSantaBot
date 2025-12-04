import os
import random
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase import create_client, Client

# Загружаем переменные окружения
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")   # ⚠️ Лучше использовать service_role key
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- Команды ---------------- #


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение"""
    welcome_message = (
        "🎅 Добро пожаловать в бот Тайного Санты!\n\n"
        "Доступные команды:\n"
        "/new_game - Создать новую игру\n"
        "/join - Присоединиться к текущей игре\n"
        "/list - Показать участников\n"
        "/start_game - Начать распределение (минимум 2 участника)\n"
        "/instructions - Инструкция по использованию\n"
        "/help - Показать это сообщение"
    )
    await update.message.reply_text(welcome_message)


async def instructions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Инструкция по использованию"""
    message = (
        "📌 *Инструкция по использованию бота Тайного Санты*\n\n"
        "1️⃣ Добавьте бота в групповой чат, где будет проходить игра.\n"
        "2️⃣ В чате напишите команду: `/new_game` — бот создаст игру.\n"
        "3️⃣ Все участники пишут `/join` в этом же чате, чтобы присоединиться.\n"
        "4️⃣ Проверьте список участников командой `/list`\n"
        "5️⃣ Когда все готовы — запустите распределение: `/start_game`\n\n"
        "⚠️ Чтобы бот мог отправить вам личное сообщение, *откройте его в Telegram и нажмите «Start»*.\n\n"
        "🎁 Приятной игры и весёлых праздников!"
    )
    await update.message.reply_markdown(message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать помощь"""
    await start(update, context)


async def new_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создать новую игру"""
    chat_id = update.effective_chat.id
    try:
        existing_game = (
            supabase.table("games")
            .select("*")
            .eq("chat_id", chat_id)
            .eq("status", "registration")
            .execute()
        )

        if existing_game.data:
            await update.message.reply_text(
                "В этом чате уже есть активная игра!\n"
                "Используйте /join чтобы присоединиться."
            )
            return

        supabase.table("games").insert(
            {"chat_id": chat_id, "status": "registration"}
        ).execute()

        await update.message.reply_text(
            "🎄 Новая игра Тайного Санты создана!\n"
            "Участники могут присоединиться командой /join\n"
            "Когда все присоединятся, используйте /start_game"
        )
    except Exception as e:
        await update.message.reply_text(f"Ошибка при создании игры: {str(e)}")


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Присоединиться к игре"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    try:
        game = (
            supabase.table("games")
            .select("*")
            .eq("chat_id", chat_id)
            .eq("status", "registration")
            .execute()
        )

        if not game.data:
            await update.message.reply_text(
                "Нет активной игры в этом чате. Используйте /new_game"
            )
            return

        game_id = game.data[0]["id"]

        existing_participant = (
            supabase.table("participants")
            .select("*")
            .eq("game_id", game_id)
            .eq("user_id", user.id)
            .execute()
        )

        if existing_participant.data:
            await update.message.reply_text("Ты уже участвуешь в этой игре!")
            return

        supabase.table("participants").insert(
            {
                "game_id": game_id,
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name or "Участник",
            }
        ).execute()

        await update.message.reply_text(
            f"🎁 {user.first_name or user.username} добавлен в список Тайного Санты!"
        )
    except Exception as e:
        await update.message.reply_text(f"Ошибка при присоединении: {str(e)}")


async def list_participants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать участников"""
    chat_id = update.effective_chat.id
    try:
        game = (
            supabase.table("games")
            .select("*")
            .eq("chat_id", chat_id)
            .eq("status", "registration")
            .execute()
        )

        if not game.data:
            await update.message.reply_text("Нет активной игры в этом чате.")
            return

        game_id = game.data[0]["id"]
        participants = (
            supabase.table("participants").select("*").eq("game_id", game_id).execute()
        )

        if not participants.data:
            await update.message.reply_text("Пока нет участников. Используйте /join")
            return

        participant_list = "\n".join(
            [
                (
                    f"{i+1}. {p['first_name']} (@{p['username']})"
                    if p["username"]
                    else f"{i+1}. {p['first_name']}"
                )
                for i, p in enumerate(participants.data)
            ]
        )

        await update.message.reply_text(
            f"🎅 Участники ({len(participants.data)}):\n\n{participant_list}"
        )
    except Exception as e:
        await update.message.reply_text(f"Ошибка при получении списка: {str(e)}")


async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запустить игру и распределить пары"""
    chat_id = update.effective_chat.id
    try:
        game = (
            supabase.table("games")
            .select("*")
            .eq("chat_id", chat_id)
            .eq("status", "registration")
            .execute()
        )

        if not game.data:
            await update.message.reply_text("Нет активной игры в этом чате.")
            return

        game_id = game.data[0]["id"]
        participants = (
            supabase.table("participants").select("*").eq("game_id", game_id).execute()
        )

        if len(participants.data) < 2:
            await update.message.reply_text(
                "Нужно минимум 2 участника для начала игры."
            )
            return

        participant_list = participants.data[:]
        random.shuffle(participant_list)

        assignments = []
        for i, giver in enumerate(participant_list):
            receiver = participant_list[(i + 1) % len(participant_list)]
            assignments.append(
                {
                    "game_id": game_id,
                    "giver_user_id": giver["user_id"],
                    "receiver_user_id": receiver["user_id"],
                }
            )

            receiver_name = (
                f"@{receiver['username']}"
                if receiver["username"]
                else receiver["first_name"]
            )

            try:
                await context.bot.send_message(
                    chat_id=giver["user_id"],
                    text=f"🎄 Ты поздравляешь {receiver_name}!\n\nПриятных праздников!",
                )
            except Exception as e:
                print(
                    f"Не удалось отправить сообщение пользователю {giver['user_id']}: {e}"
                )

        supabase.table("assignments").insert(assignments).execute()
        supabase.table("games").update(
            {"status": "completed", "started_at": datetime.utcnow().isoformat()}
        ).eq("id", game_id).execute()

        await update.message.reply_text(
            f"✅ Распределение завершено!\n"
            f"Всем {len(participant_list)} участникам отправлены личные сообщения.\n\n"
            f"🎅🎁 Приятных праздников!"
        )
    except Exception as e:
        await update.message.reply_text(f"Ошибка при запуске игры: {str(e)}")


# ---------------- Запуск ---------------- #


def main():
    """Запуск бота"""
    if not TELEGRAM_BOT_TOKEN:
        print("Ошибка: Установите TELEGRAM_BOT_TOKEN в файле .env")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("instructions", instructions))
    app.add_handler(CommandHandler("new_game", new_game))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("list", list_participants))
    app.add_handler(CommandHandler("start_game", start_game))

    print("Бот запущен и ожидает команды...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
