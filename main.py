"""
Manipulador do Telegram para o Financial Categorizer Bot
"""

import os

from dotenv import load_dotenv
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, Defaults

from src.handlers.handle_document import handle_document
from src.handlers.start import start
from src.handlers.error_handler import on_error
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

REQUIRED_ENV_VARS = [
    "BOT_TOKEN_TELEGRAM",
    "GOOGLE_API_KEY",
]

missing_env = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
if missing_env:
    logger.error(f"Variáveis de ambiente ausentes: {', '.join(missing_env)}")
    raise SystemExit(1)

TOKEN = os.getenv("BOT_TOKEN_TELEGRAM")


def main():
    defaults = Defaults(parse_mode=ParseMode.MARKDOWN)
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .defaults(defaults)
        .build()
    )

    app.add_handler(CommandHandler("start", start))

    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    app.add_error_handler(on_error)

    logger.info("Iniciando o Financial Categorizer Bot...")

    app.run_polling()


if __name__ == "__main__":
    main()
