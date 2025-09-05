"""
Manipulador do Telegram para o Financial Categorizer Bot
"""

import os
from dotenv import load_dotenv

from src.utils.logger import get_logger

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext

load_dotenv()
logger = get_logger(__name__)

async def start(update: Update, context: CallbackContext):
  logger.info(f"Usuário {update.message.from_user.id} iniciou o bot.")
  await update.message.reply_text(
    "Olá!\n\n"
    "Eu sou o Financial Categorizer Bot.\n\n"
    "Envie um arquivo CSV ou OFX para que eu possa processar.\n",
)

def main():
  TOKEN = os.getenv("BOT_TOKEN_TELEGRAM")

  if not TOKEN:
    logger.error("Token de acesso ao bot do Telegram não encontrado.")

  app = ApplicationBuilder().token(TOKEN).build()

  app.add_handler(CommandHandler("start", start))

  logger.info("Iniciando o Financial Categorizer Bot...")

  app.run_polling()

if __name__ == "__main__":
  main()
