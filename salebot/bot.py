import logging
import os
import re

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from agent import run_agent
from memory import (
    append_message,
    clear_history,
    get_history,
    get_language,
    set_language,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN: str | None = os.getenv("TELEGRAM_BOT_TOKEN")
ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")


def _detect_language(text: str) -> str | None:
    """Detect if text contains Burmese Unicode characters (U+1000–U+109F)."""
    for char in text:
        if "\u1000" <= char <= "\u109f":
            return "my"
    return "en"


def _build_language_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en")],
        [InlineKeyboardButton("မြန်မာ 🇲🇲", callback_data="lang_my")],
    ]
    return InlineKeyboardMarkup(keyboard)


WELCOME = (
    "👋 Welcome to *Travelbase Assistant*\\!\n\n"
    "I can build a personalised tour package for you — flights, hotels, activities, "
    "and transport — all within your budget\\.\n\n"
    "Just tell me something like:\n"
    '_"I want to visit Singapore this weekend, my budget is \\$1000"_\n\n'
    "Or ask me anything about travelling in Southeast Asia\\.\n\n"
    "Type /clear to start a fresh conversation\\."
)

LANG_SELECT = "🌐 Please select your language:\\n\nဘာသာစကားကို ရွေးချယ်ပါ\\:"

EN_CONFIRM = "Language set to English\\. How can I help you today?"
MY_CONFIRM = "ဘာသာစကားကို မြန်မာလို သတ်မှတ်လိုက်ပါပြီ။\\ ဒီနေ့ ဘာများ ကူညီပေးရမလဲခင်ဗျာ။\\"
EN_READY = "How can I help you today?"
MY_READY = "ဒီနေ့ ဘာများ ကူညီပေးရမလဲခင်ဗျာ။"

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
    await update.message.reply_text(
        LANG_SELECT,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=_build_language_keyboard(),
    )


async def language_callback_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.callback_query is None:
        return
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data or ""

    await query.answer()

    if data == "lang_en":
        set_language(user_id, "en")
        await query.edit_message_text(EN_CONFIRM, parse_mode=ParseMode.MARKDOWN_V2)
        logger.info(f"User {user_id} set language to English")
    elif data == "lang_my":
        set_language(user_id, "my")
        await query.edit_message_text(MY_CONFIRM, parse_mode=ParseMode.MARKDOWN_V2)
        logger.info(f"User {user_id} set language to Burmese")
    else:
        return

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=EN_READY if get_language(user_id) == "en" else MY_READY,
        parse_mode=ParseMode.MARKDOWN_V2,
    )


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

    lang = get_language(user_id)
    if lang is None:
        detected = _detect_language(user_message)
        set_language(user_id, detected)
        lang = detected
        logger.info(f"User {user_id} auto-detected language: {lang}")

    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING,
        )

        history = get_history(user_id)
        response = await run_agent(user_id, user_message, history, lang=lang)

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
    app.add_handler(CallbackQueryHandler(language_callback_handler, pattern="^lang_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_error_handler(error_handler)

    logger.info("Travelbase bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
