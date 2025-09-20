"""
Mensagens padronizadas específicas para interações do bot do Telegram.
"""


class TelegramMessages:
    # Mensagens genéricas/erros de entrada
    INVALID_INPUT = (
        "O arquivo enviado não é suportado. Por favor, envie um arquivo CSV ou OFX."
    )

    # Mensagens de boas-vindas/comandos
    WELCOME = (
        "Olá!\n\n"
        "Eu sou o Financial Categorizer Bot.\n\n"
        "Envie um arquivo CSV ou OFX para que eu possa processar.\n"
    )

    # Confirmações de recebimento
    RECEIVED_FILE = "📄 Recebi o arquivo **{file_name}**.\n\n"
    DETECTED_TYPE = "Tipo detectado: {file_type}."

    # Avisos de tipo não suportado
    UNSUPPORTED_FILE = (
        "📄 O arquivo **{file_name}** não é suportado.\n"
        "Por favor, envie apenas arquivos CSV ou OFX."
    )


