"""
Manipulador do Telegram para o Financial Categorizer Bot
"""

import os
from dotenv import load_dotenv

from src.utils.logger import get_logger

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from src.handlers.bot_defs.start import start
from src.handlers.bot_defs.handle_document import handle_document

load_dotenv()
logger = get_logger(__name__)

def main():
  TOKEN = os.getenv("BOT_TOKEN_TELEGRAM")

  if not TOKEN:
    logger.error("Token de acesso ao bot do Telegram não encontrado.")

  app = ApplicationBuilder().token(TOKEN).build()

  app.add_handler(CommandHandler("start", start))

  app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

  logger.info("Iniciando o Financial Categorizer Bot...")

  app.run_polling()

if __name__ == "__main__":
  main()
