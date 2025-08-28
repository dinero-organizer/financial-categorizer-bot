# Infrastructure

Infrastructure as Code for Financial Categorizer Bot.

## Structure

```
infra/
├── template.yaml      # SAM template
├── samconfig.toml     # SAM configuration
├── deploy.sh          # Deployment script
└── environments/      # Environment configs
```

## Deployment

### GitHub Actions
1. Go to Actions → Deploy Financial Bot
2. Run workflow
3. Select environment (dev/staging/prod)

Required secrets:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`  
- `TELEGRAM_BOT_TOKEN`

### Local
```bash
./deploy.sh dev
./deploy.sh staging
./deploy.sh prod
```

## Resources

**Lambda Function**
- Name: `financial-bot-{env}`
- Runtime: Python 3.11
- Timeout: 30s

**API Gateway**
- Name: `financial-bot-api-{env}`
- Endpoint: `/webhook` (POST)

**S3 Bucket**
- Name: `financial-bot-documents-{env}`
- Lifecycle: 30 days

**CloudWatch**
- Log Group: `/aws/lambda/financial-bot-{env}`
- Retention: 14 days

## Configuration

Set webhook URL in Telegram after deployment:

```bash
curl -X POST "https://api.telegram.org/bot{BOT_TOKEN}/setWebhook" \
  -d '{"url": "{WEBHOOK_URL}"}'
```

## Monitoring

```bash
# Logs
sam logs --stack-name financial-bot-dev --tail

# Local testing
sam local start-api --template template.yaml
```
