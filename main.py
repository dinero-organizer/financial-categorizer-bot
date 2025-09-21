"""
Manipulador do Telegram para o Financial Categorizer Bot
"""

import os

from dotenv import load_dotenv
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from src.handlers.bot_defs.handle_document import handle_document
from src.handlers.bot_defs.start import start
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

TOKEN = os.getenv("BOT_TOKEN_TELEGRAM")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

missing_env = []
if not TOKEN:
    missing_env.append("BOT_TOKEN_TELEGRAM")
if not GOOGLE_API_KEY:
    missing_env.append("GOOGLE_API_KEY")

if missing_env:
    logger.error(f"Variáveis de ambiente ausentes: {', '.join(missing_env)}")
    raise SystemExit(1)


def main():
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .parse_mode(ParseMode.MARKDOWN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))

    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    logger.info("Iniciando o Financial Categorizer Bot...")

    app.run_polling()


if __name__ == "__main__":
    main()
