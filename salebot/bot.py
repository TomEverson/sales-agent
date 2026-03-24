import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from agent import handle_message
from memory import clear_history

load_dotenv()

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

WELCOME = (
    "👋 Welcome to *Travelbase*!\n\n"
    "I'm your personal travel assistant for Southeast Asia. "
    "Tell me where you want to go, your budget, and how long you're travelling — "
    "and I'll put together a great package for you.\n\n"
    "Example: _\"I want to visit Bali for 5 days with a $600 budget\"_\n\n"
    "Type /clear to start a new conversation."
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    await update.message.reply_text(WELCOME, parse_mode=ParseMode.MARKDOWN)


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.effective_user is None:
        return
    clear_history(update.effective_user.id)
    await update.message.reply_text(
        "🗑 Conversation cleared. Let's start fresh — where do you want to go?"
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.effective_user is None:
        return

    user_id = update.effective_user.id
    user_text = update.message.text or ""

    if not user_text.strip():
        return

    # Show typing indicator while processing
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,  # type: ignore[union-attr]
        action=ChatAction.TYPING,
    )

    response = await handle_message(user_id, user_text)

    await update.message.reply_text(
        response,
        parse_mode=ParseMode.MARKDOWN,
    )


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set in .env")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    logger.info("Travelbase bot is running...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
