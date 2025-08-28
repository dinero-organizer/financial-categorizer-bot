#!/bin/bash

# Script de deployment para Financial Categorizer Bot
# Uso: ./deploy.sh [dev|staging|prod]
# Execute da pasta infra/

ENVIRONMENT=${1:-dev}

echo "🚀 Deploying Financial Bot to $ENVIRONMENT environment..."

# Verificar se SAM está instalado
if ! command -v sam &> /dev/null; then
    echo "❌ SAM CLI não encontrado. Instale com: pip install aws-sam-cli"
    exit 1
fi

# Verificar se AWS CLI está configurado
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI não configurado. Configure suas credenciais."
    exit 1
fi

# Build da aplicação (volta para a raiz do projeto)
echo "📦 Building application..."
cd ..
sam build --template infra/template.yaml --build-dir infra/.aws-sam/build
cd infra

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

# Deploy baseado no ambiente
echo "🌍 Deploying to $ENVIRONMENT..."

# No GitHub Actions, não precisa de confirmação interativa
if [ ! -z "$GITHUB_ACTIONS" ]; then
    sam deploy --config-env $ENVIRONMENT --no-confirm-changeset
else
    # Deploy local ainda pede confirmação para prod
    if [ "$ENVIRONMENT" = "prod" ]; then
        echo "⚠️  ATENÇÃO: Deploy para PRODUÇÃO!"
        read -p "Tem certeza? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ Deploy cancelado"
            exit 1
        fi
        sam deploy --config-env prod --no-confirm-changeset
    else
        sam deploy --config-env $ENVIRONMENT
    fi
fi

if [ $? -eq 0 ]; then
    echo "✅ Deploy successful!"
    
    # Mostrar URL do webhook
    WEBHOOK_URL=$(aws cloudformation describe-stacks \
        --stack-name "financial-bot-$ENVIRONMENT" \
        --query 'Stacks[0].Outputs[?OutputKey==`WebhookUrl`].OutputValue' \
        --output text)
    
    echo "🔗 Webhook URL: $WEBHOOK_URL"
    echo "📋 Configure este URL no seu bot do Telegram"
else
    echo "❌ Deploy failed"
    exit 1
fi
