from src.utils.logger import get_logger

from telegram import Update
from telegram.ext import ContextTypes
from src.config.messages import TelegramMessages

import os
import json
import tempfile
from pathlib import Path
from datetime import datetime
import shutil

from src.parsers.csv import parse_csv_bank_statement
from src.parsers.ofx import parse_ofx_file
from src.ai.transaction_classifier import categorize_with_gemini
import boto3


logger = get_logger(__name__)


MAX_FILE_SIZE_MB = 10


def _detect_file_type(file_name: str):
  """Retorna 'csv' | 'ofx' ou None com base na extensão."""
  lower = (file_name or "").lower()
  if lower.endswith(".csv"):
    return "csv"
  if lower.endswith(".ofx"):
    return "ofx"
  return None


def _sanitize_filename(name: str) -> str:
  """Garante que apenas o nome-base seja usado, sem diretórios."""
  return Path(name or "arquivo").name


async def _download_document_to_temp(context: ContextTypes.DEFAULT_TYPE, document, dest_dir: str) -> str:
  """Baixa o arquivo do Telegram para um diretório temporário e retorna o caminho local."""
  # Verifica tamanho
  try:
    file_size = int(getattr(document, "file_size", 0) or 0)
  except Exception:
    file_size = 0
  if file_size and file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
    raise ValueError(f"Arquivo excede o limite de {MAX_FILE_SIZE_MB}MB")

  safe_name = _sanitize_filename(document.file_name)
  local_path = Path(dest_dir) / safe_name
  tg_file = await context.bot.get_file(document.file_id)
  await tg_file.download_to_drive(local_path)
  logger.info(f"Arquivo baixado para {local_path}")
  return local_path


def _parse_file_to_statement(file_path: str, file_type: str):
  """Parseia o arquivo (CSV/OFX) e retorna um ParsedBankStatement."""
  if file_type == "csv":
    return parse_csv_bank_statement(file_path)
  if file_type == "ofx":
    return parse_ofx_file(file_path)
  raise ValueError(f"Tipo de arquivo não suportado: {file_type}")


def _statement_to_transactions(statement) -> list:
  """Converte ParsedBankStatement -> List[dict] esperado pelo classificador."""
  return [
    {
      "id": expense.id,
      "name": expense.name,
      "value": float(expense.value),
      "date": expense.date.isoformat(),
    }
    for expense in statement.expenses
  ]


def _categorize_with_ai(transactions: list) -> tuple:
  """Tenta categorizar via Gemini. Retorna (transactions, ai_ok)."""
  try:
    categorized = categorize_with_gemini(transactions)
    return categorized, True
  except Exception as e:
    logger.error(f"Falha ao categorizar com Gemini: {e}")
    fallback = [
      {
        **tx,
        "category": "Não categorizada",
        "categorization_confidence": 0.0,
        "categorization_reasoning": "AI indisponível",
      }
      for tx in transactions
    ]
    return fallback, False


def _build_result_payload(file_name: str, file_type: str, categorized_transactions: list) -> dict:
  """Monta o payload final de resultado para persistência/envio."""
  return {
    "original_file": file_name,
    "processed_at": datetime.utcnow().isoformat() + "Z",
    "file_type": file_type,
    "total_transactions": len(categorized_transactions),
    "transactions": categorized_transactions,
  }


def _write_result_json(dest_dir: str, file_stem: str, result: dict) -> str:
  """Escreve o JSON de resultado e retorna o caminho gerado."""
  result_path = Path(dest_dir) / f"{file_stem}_categorized.json"
  with open(result_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
  return result_path


def _is_debug_mode() -> bool:
  """Determina se estamos em modo de debug via variáveis de ambiente.

  Regras:
  - Se DEBUG for verdadeiro (1/true/yes/on), considera debug.
  - Caso contrário, se APP_ENV/ENVIRONMENT for 'production'/'prod', NÃO é debug.
  - Demais ambientes são considerados debug por padrão.
  """
  debug_val = (os.getenv("DEBUG", "").strip().lower())
  if debug_val in ("1", "true", "yes", "on"):
    return True

  env_val = (os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "development")).strip().lower())
  if env_val in ("production", "prod"):
    return False

  return True


def _should_cleanup_tmp() -> bool:
  """Remove arquivos temporários somente quando NÃO estiver em debug."""
  return not _is_debug_mode()


def _upload_to_s3(local_path: Path, user_id: int, file_name: str) -> str:
  bucket = os.getenv("S3_BUCKET_UPLOADS")
  if not bucket:
    return ""
  
  s3 = boto3.client("s3")
  key = f"uploads/{user_id}/{datetime.utcnow().strftime('%Y%m%d%H%M%S')}/{file_name}"
  s3.upload_file(str(local_path), bucket, key)
  return f"s3://{bucket}/{key}"


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
  document = update.message.document

  if not document:
    await update.message.reply_text(TelegramMessages.INVALID_INPUT)
    return
  
  file_name = _sanitize_filename(document.file_name)
  user_id = update.message.from_user.id

  logger.info(f"Usuário {user_id} enviou o arquivo {file_name}")

  file_type = _detect_file_type(file_name)

  if file_type in ("csv", "ofx"):
    await update.message.reply_text(
      TelegramMessages.RECEIVED_FILE.format(file_name=file_name)
      + TelegramMessages.DETECTED_TYPE.format(file_type=file_type.upper())
    )

    # Cria diretório temporário e caminho local do arquivo
    tmp_dir = tempfile.mkdtemp(prefix="fin-cat-")

    try:
      # Baixa o arquivo recebido do Telegram
      local_path = await _download_document_to_temp(context, document, tmp_dir)

      _ = _upload_to_s3(Path(local_path), user_id, file_name)

      # Faz o parse de acordo com o tipo
      statement = _parse_file_to_statement(local_path, file_type)

      # Converte para o formato esperado pelo AI
      transactions = _statement_to_transactions(statement)

      # Chama o classificador (Gemini)
      categorized_transactions, ai_ok = _categorize_with_ai(transactions)

      # Monta resultado e envia ao usuário
      result = _build_result_payload(file_name, file_type, categorized_transactions)
      result_path = _write_result_json(tmp_dir, Path(file_name).stem, result)

      caption_lines = [
        "✅ Processamento concluído!",
        f"Transações: {len(categorized_transactions)}",
      ]
      if not ai_ok:
        caption_lines.append("⚠️ Categorização por AI não disponível no momento.")

      with open(result_path, "rb") as f:
        await update.message.reply_document(
          document=f,
          filename=Path(result_path).name,
          caption="\n".join(caption_lines),
        )

    except Exception as e:
      logger.error(f"Erro ao processar arquivo '{file_name}': {e}")
      await update.message.reply_text(
        f"❌ Ocorreu um erro ao processar o arquivo: {str(e)}"
      )
    finally:
      if _should_cleanup_tmp():
        try:
          shutil.rmtree(tmp_dir, ignore_errors=True)
          logger.info(f"Diretório temporário removido: {tmp_dir}")
        except Exception as cleanup_err:
          logger.warning(f"Falha ao remover diretório temporário {tmp_dir}: {cleanup_err}")
      else:
        logger.info(f"Mantendo arquivos temporários para debug em: {tmp_dir}")

  else:
    await update.message.reply_text(
      TelegramMessages.UNSUPPORTED_FILE.format(file_name=file_name)
    )