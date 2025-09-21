from src.utils.logger import get_logger
from src.config.messages import TelegramMessages

from telegram import Update
from telegram.ext import ContextTypes

logger = get_logger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  logger.info(f"Usuário {update.message.from_user.id} iniciou o bot.")
  
  await update.message.reply_text(TelegramMessages.WELCOME)