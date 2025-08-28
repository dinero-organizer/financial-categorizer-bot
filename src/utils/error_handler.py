"""
Error handling padronizado para o Financial Categorizer Bot
"""

import json
from typing import Dict, Any, Optional
from .logger import get_logger, Messages

logger = get_logger(__name__)


class ErrorHandler:
    """Classe para padronizar tratamento de erros no Lambda"""
    
    @staticmethod
    def lambda_response(status_code: int, message: str, error_details: Optional[str] = None) -> Dict[str, Any]:
        """Cria resposta padronizada do Lambda"""
        body = {'message': message}
        
        if error_details and status_code >= 400:
            logger.error(f"{message} - Detalhes: {error_details}")
            # Não expor detalhes internos para o usuário
            body = {'error': message}
        else:
            logger.info(message)
            
        return {
            'statusCode': status_code,
            'body': json.dumps(body),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    
    @staticmethod
    def handle_file_error(error: Exception, filename: str = "desconhecido") -> Dict[str, Any]:
        """Trata erros específicos de arquivo"""
        if isinstance(error, FileNotFoundError):
            logger.error(Messages.FILE_NOT_FOUND.format(filename=filename))

            return ErrorHandler.lambda_response(404, "Arquivo não encontrado")
        
        elif isinstance(error, ValueError):
            logger.error(Messages.FILE_INVALID_FORMAT.format(format=filename.split('.')[-1]))

            return ErrorHandler.lambda_response(400, "Formato de arquivo inválido")
        
        elif isinstance(error, MemoryError):
            logger.error(Messages.FILE_TOO_LARGE.format(size="?", max_size="10"))

            return ErrorHandler.lambda_response(413, "Arquivo muito grande")
        
        else:
            logger.error(f"Erro inesperado no arquivo {filename}: {str(error)}")

            return ErrorHandler.lambda_response(500, "Erro interno do servidor", str(error))
    
    @staticmethod
    def handle_aws_error(error: Exception, service: str) -> Dict[str, Any]:
        """Trata erros específicos da AWS"""
        logger.error(Messages.AWS_CONNECTION_ERROR.format(service=service))
        logger.error(f"Detalhes do erro AWS: {str(error)}")

        return ErrorHandler.lambda_response(503, f"Serviço {service} temporariamente indisponível")
    
    @staticmethod
    def handle_telegram_error(error: Exception) -> Dict[str, Any]:
        """Trata erros específicos do Telegram"""
        logger.error(Messages.TELEGRAM_API_ERROR.format(error=str(error)))
        
        return ErrorHandler.lambda_response(502, "Erro na comunicação com Telegram")
    
    @staticmethod
    def handle_generic_error(error: Exception, context: str = "processamento") -> Dict[str, Any]:
        """Trata erros genéricos"""
        logger.error(f"Erro durante {context}: {str(error)}")
        
        return ErrorHandler.lambda_response(500, "Erro interno do servidor", str(error))


def handle_errors(error_type: str = "generic"):
    """Decorator para capturar e tratar erros automaticamente"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if error_type == "file":
                    return ErrorHandler.handle_file_error(e)
                elif error_type == "aws":
                    return ErrorHandler.handle_aws_error(e, "AWS")
                elif error_type == "telegram":
                    return ErrorHandler.handle_telegram_error(e)
                else:
                    return ErrorHandler.handle_generic_error(e, func.__name__)
        return wrapper
    return decorator
