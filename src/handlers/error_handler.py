from src.utils.logger import get_logger

from telegram import Update
from telegram.ext import ContextTypes
from src.config.messages import TelegramMessages


logger = get_logger(__name__)


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE):
  logger.error("Unhandled exception in handler", exc_info=context.error)

  try:
    if isinstance(update, Update) and update.effective_message:
      await update.effective_message.reply_text(TelegramMessages.ERROR_GENERIC)
  except Exception:
    # Evita loop de erros
    pass


