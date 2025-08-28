"""
Auxiliares AWS para a função Lambda
"""

import boto3
import json
from typing import Dict, Any


def send_telegram_message(chat_id: str, text: str) -> Dict[str, Any]:
    """Send message back to Telegram (BOT-003: Response System)"""
    # TODO: Implement Telegram API call
    return {'message': 'Mensagem enviada'}


def categorize_with_bedrock(transaction_text: str) -> Dict[str, Any]:
    """Use Bedrock to categorize transaction (AI-001, AI-002, AI-003)"""
    # TODO: Implement Bedrock categorization
    return {'category': 'Desconhecido', 'confidence': 0.0}


def extract_text_with_textract(s3_bucket: str, s3_key: str) -> str:
    """Extract text from PDF/image using Textract (FILE-003)"""
    # TODO: Implement Textract OCR
    return "Texto extraído"
