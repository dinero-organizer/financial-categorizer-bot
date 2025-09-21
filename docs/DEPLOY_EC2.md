# Deploy em EC2 via SAM + Makefile

Este projeto é implantado em EC2 utilizando AWS SAM, acionado via Makefile.

## Pré-requisitos
- AWS CLI e SAM CLI instalados e configurados
- Credenciais AWS válidas no ambiente local/CI

## Comandos (Makefile)
- Build:
```
make sam-build
```
- Deploy (dev):
```
make sam-deploy-dev
```
- Deploy (prod):
```
make sam-deploy-prod
```

## Parâmetros por ambiente
- Arquivos `infra/environments/dev.json` e `infra/environments/prod.json` definem `Environment` e `TelegramBotToken`.

## Variáveis de ambiente em runtime
- O SAM deve injetar:
  - `BOT_TOKEN_TELEGRAM`
  - `GOOGLE_API_KEY`
  - `APP_ENV`
  - `S3_BUCKET_UPLOADS`

## Observações
- Ajuste `infra/template.yaml` para o modelo de EC2 aprovado (Launch Template/Auto Scaling) e policies de IAM necessárias (acesso ao S3 e CloudWatch).
