from src.utils.logger import get_logger

from telegram import Update
from telegram.ext import ContextTypes

logger = get_logger(__name__)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
  document = update.message.document

  if not document:
    await update.message.reply_text(Messages.INVALID_INPUT)
    return
  
  file_name = document.file_name
  user_id = update.message.from_user.id

  logger.info(f"Usuário {user_id} enviou o arquivo {file_name}")

  if file_name.endswith(".csv"):
    await update.message.reply_text(
      f"📄 Recebi o arquivo **{file_name}**.\n\n"
      "Tipo detectado: CSV."
    )

    # TODO: Implementar processamento de arquivo CSV
  elif file_name.endswith(".ofx"):
    await update.message.reply_text(
      f"📄 Recebi o arquivo **{file_name}**.\n\n"
      "Tipo detectado: OFX."
    )

    # TODO: Implementar processamento de arquivo OFX
  else:
    await update.message.reply_text(
      f"📄 O arquivo **{file_name}** não é suportado.\n"
      "Por favor, envie apenas arquivos CSV ou OFX."
    )