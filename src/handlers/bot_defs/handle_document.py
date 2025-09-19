from src.utils.logger import get_logger

from telegram import Update
from telegram.ext import ContextTypes
from src.handlers.messages import TelegramMessages

logger = get_logger(__name__)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
  document = update.message.document

  if not document:
    await update.message.reply_text(TelegramMessages.INVALID_INPUT)
    return
  
  file_name = document.file_name
  user_id = update.message.from_user.id

  logger.info(f"Usuário {user_id} enviou o arquivo {file_name}")

  if file_name.endswith(".csv"):
    await update.message.reply_text(
      TelegramMessages.RECEIVED_FILE.format(file_name=file_name)
      + TelegramMessages.DETECTED_TYPE.format(file_type="CSV")
    )

    # TODO: Implementar processamento de arquivo CSV
  elif file_name.endswith(".ofx"):
    await update.message.reply_text(
      TelegramMessages.RECEIVED_FILE.format(file_name=file_name)
      + TelegramMessages.DETECTED_TYPE.format(file_type="OFX")
    )

    # TODO: Implementar processamento de arquivo OFX
  else:
    await update.message.reply_text(
      TelegramMessages.UNSUPPORTED_FILE.format(file_name=file_name)
    )