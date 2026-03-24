import logging
import os
import re

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from agent import run_agent
from memory import append_message, clear_history, get_history

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN: str | None = os.getenv("TELEGRAM_BOT_TOKEN")
ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")

WELCOME = (
    "👋 Welcome to *Travelbase Assistant*\\!\n\n"
    "I can build a personalised tour package for you — flights, hotels, activities, "
    "and transport — all within your budget\\.\n\n"
    "Just tell me something like:\n"
    "_\"I want to visit Singapore this weekend, my budget is \\$1000\"_\n\n"
    "Or ask me anything about travelling in Southeast Asia\\.\n\n"
    "Type /clear to start a fresh conversation\\."
)

_MD_SPECIAL = re.compile(r"([\\\_*\[\]()~`>#+\-=|{}.!])")


def escape_markdown(text: str) -> str:
    """Escape all MarkdownV2 special characters."""
    return _MD_SPECIAL.sub(r"\\\1", text)


def _validate_env() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set in .env")
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is not set in .env")


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    await update.message.reply_text(WELCOME, parse_mode=ParseMode.MARKDOWN_V2)


async def clear_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.effective_user is None:
        return
    user_id = update.effective_user.id
    clear_history(user_id)
    logger.info(f"History cleared for user {user_id}")
    await update.message.reply_text(
        "🗑 Conversation cleared. Let's start fresh — where would you like to go?"
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.effective_user is None:
        return

    user_id = update.effective_user.id
    user_message = update.message.text or ""

    if not user_message.strip():
        return

    logger.info(f"Message from user {user_id}: {user_message[:50]}")

    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING,
        )

        history = get_history(user_id)
        response = await run_agent(user_id, user_message, history)

        append_message(user_id, "user", user_message)
        append_message(user_id, "assistant", response)

        logger.info(f"Response to user {user_id}: {response[:50]}")

        await update.message.reply_text(
            escape_markdown(response),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    except Exception:
        await update.message.reply_text(
            "Sorry, something went wrong. Please try again in a moment."
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Update {update} caused error {context.error}")
    if update and isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "An unexpected error occurred. Please try again."
        )


def main() -> None:
    _validate_env()

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()  # type: ignore[arg-type]

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("clear", clear_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_error_handler(error_handler)

    logger.info("Travelbase bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
