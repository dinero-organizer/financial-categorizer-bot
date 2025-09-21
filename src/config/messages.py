"""
Mensagens padronizadas específicas para interações do bot do Telegram.
"""


class TelegramMessages:
    # Mensagens genéricas/erros de entrada
    INVALID_INPUT = (
        "⚠️ O arquivo enviado não é suportado.\n"
        "Envie um arquivo nos formatos **CSV** ou **OFX** para continuar."
    )

    # Mensagens de boas-vindas/comandos
    WELCOME = (
        "👋 Olá, seja bem-vindo!\n\n"
        "Eu sou o *Financial Categorizer Bot* 🤖💰\n\n"
        "Aqui você pode enviar seus arquivos **CSV** ou **OFX** "
        "para que eu processe suas transações e gere relatórios categorizados. 🚀"
    )

    # Confirmações de recebimento
    RECEIVED_FILE = (
        "✅ Arquivo **{file_name}** recebido com sucesso!\n\n"
        "🔍 Analisando o conteúdo..."
    )

    DETECTED_TYPE = "📂 Tipo de arquivo detectado: **{file_type}**."

    # Avisos de tipo não suportado
    UNSUPPORTED_FILE = (
        "❌ Não consegui processar o arquivo **{file_name}**.\n\n"
        "👉 Somente arquivos nos formatos **CSV** ou **OFX** são aceitos.\n"
        "Por favor, tente novamente com um desses formatos. 😉"
    )
