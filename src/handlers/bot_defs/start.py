from src.utils.logger import get_logger

from telegram import Update
from telegram.ext import CallbackContext

logger = get_logger(__name__)

async def start(update: Update, context: CallbackContext):
  logger.info(f"Usuário {update.message.from_user.id} iniciou o bot.")
  
  await update.message.reply_text(
    "Olá!\n\n"
    "Eu sou o Financial Categorizer Bot.\n\n"
    "Envie um arquivo CSV ou OFX para que eu possa processar.\n",
)