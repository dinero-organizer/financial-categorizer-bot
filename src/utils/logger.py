import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_logger(name: str) -> logging.Logger:
    """Obtém um logger com o nome fornecido."""
    logger = logging.getLogger(name)
    return logger


class Messages:
    """Mensagens padronizadas em português para logs e erros"""
    
    # Erros de arquivo
    FILE_NOT_FOUND = "Arquivo não encontrado: {filename}"
    FILE_INVALID_FORMAT = "Formato de arquivo inválido: {format}"
    FILE_TOO_LARGE = "Arquivo muito grande: {size}MB (máximo: {max_size}MB)"
    
    # Erros de processamento
    PARSE_ERROR = "Erro ao processar arquivo: {error}"
    TRANSACTION_INVALID = "Transação inválida: {transaction}"
    
    # Sucesso
    FILE_PROCESSED = "Arquivo processado com sucesso: {count} transações"
    CATEGORIZATION_COMPLETE = "Categorização concluída: {category}"
    
    # AWS/API
    AWS_CONNECTION_ERROR = "Erro de conexão com AWS: {service}"
    TELEGRAM_API_ERROR = "Erro na API do Telegram: {error}"
    
    # Informações
    PROCESSING_START = "Iniciando processamento de {type}"
    PROCESSING_COMPLETE = "Processamento concluído em {duration}s"