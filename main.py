"""
AWS Lambda handler for Financial Categorizer Telegram Bot
"""

import json
from typing import Dict, Any

from src.utils.logger import get_logger, Messages
from src.utils.error_handler import ErrorHandler, handle_errors
from src.handlers.bot_defs.handle_document import handle_document

logger = get_logger(__name__)

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Main Lambda handler for Telegram webhook.
    """

    logger.info(f"Evento recebido: {event}")
    logger.info(f"Contexto: {context}")

    try:
        # Parse Telegram webhook data
        body = json.loads(event.get('body', '{}'))
        message = body.get('message', {})
        
        # Route based on message type
        if 'document' in message:
            return handle_file_upload(message)
        elif 'photo' in message:
            return handle_image_upload(message)
        else:
            return handle_text_message(message)
            
    except Exception as e:
        return ErrorHandler.handle_generic_error(e, "webhook")


@handle_errors("file")
def handle_file_upload(message: Dict[str, Any]) -> Dict[str, Any]:
    """Handle CSV/OFX file uploads"""
    status, message = handle_document(message)
    return ErrorHandler.lambda_response(400, "Processamento de arquivos ainda não implementado")


def handle_image_upload(message: Dict[str, Any]) -> Dict[str, Any]:
    """Handle image/PDF uploads"""
    return {'statusCode': 400, 'body': json.dumps({'message': Messages.INVALID_INPUT})}


def handle_text_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """Handle text messages"""
    return {'statusCode': 400, 'body': json.dumps({'message': Messages.INVALID_INPUT})}


if __name__ == "__main__":
    mock_event = {
        'body': json.dumps({
            'message': {
                'text': 'Olá bot!',
                'chat': {'id': 123}
            }
        })
    }

    logger.info("-" * 50)
    logger.info("Rodando lambda com evento mockado...")
    logger.info("-" * 50)
    result = lambda_handler(mock_event, None)
    logger.info(f"Result: {result}")
    logger.info("-" * 50)
    logger.info("Bot lambda terminou.")
    logger.info("-" * 50)
