"""
Manipulador do Telegram para o Financial Categorizer Bot
"""

from src.utils.logger import get_logger

from telegram.ext import ApplicationBuilder, CommandHandler

logger = get_logger(__name__)

def main():
  TOKEN = "8323730258:AAGMJBoywxGKphut0QrkLA_ySLgjaK7O-h4"

  if not TOKEN:
    logger.error("Token de acesso ao bot do Telegram não encontrado.")

  app = ApplicationBuilder().token(TOKEN).build()

  logger.info("Iniciando o Financial Categorizer Bot...")

  app.run_polling()

if __name__ == "__main__":
  main()
