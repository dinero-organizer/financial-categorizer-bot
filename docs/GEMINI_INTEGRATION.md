# Integração Gemini para Categorização de Transações

Este documento explica como usar a integração do Google Gemini para categorizar automaticamente uma lista de transações financeiras.

## Visão Geral

A integração permite categorizar transações financeiras usando a API do Google Gemini, oferecendo categorização inteligente baseada na descrição das transações.

## Configuração

### 1. Instalar Dependências

```bash
pip install google-generativeai>=0.3.0
```

### 2. Configurar API Key

Configure a variável de ambiente com sua chave da API Google:

```bash
export GOOGLE_API_KEY="sua-chave-google-aqui"
```

Ou no código Python:

```python
import os
os.environ['GOOGLE_API_KEY'] = 'sua-chave-google-aqui'
```

## Uso Básico

### Categorizar Lista de Transações

```python
from src.ai.transaction_classifier import categorize_with_gemini

# Lista de transações em formato JSON
transactions = [
    {
        "id": 1,
        "name": "Uber *uber.com.br",
        "value": -15.50,
        "date": "2024-01-15"
    },
    {
        "id": 2,
        "name": "Restaurante Sushi Bar", 
        "value": -89.90,
        "date": "2024-01-14"
    },
    {
        "id": 3,
        "name": "Salário Janeiro",
        "value": 3500.00,
        "date": "2024-01-05"
    },
    {
        "id": 4,
        "name": "Farmácia São João",
        "value": -45.30,
        "date": "2024-01-12"
    },
    {
        "id": 5,
        "name": "Netflix",
        "value": -32.90,
        "date": "2024-01-10"
    }
]

# Categoriza as transações
categorized_transactions = categorize_with_gemini(transactions)

# Resultado
for tx in categorized_transactions:
    print(f"• {tx['name']}")
    print(f"  💰 Valor: R$ {tx['value']:.2f}")
    print(f"  📂 Categoria: {tx['category']}")
    print(f"  🎯 Confiança: {tx['categorization_confidence']}")
    print(f"  💭 Justificativa: {tx['categorization_reasoning']}")
    print()
```


## Formato dos Dados

### Entrada (Transações)

```json
[
    {
        "id": 1,
        "name": "Descrição da transação",
        "value": -15.50,
        "date": "2024-01-15",
        "category": "Não categorizada"  // opcional
    }
]
```

### Saída (Transações Categorizadas)

```json
[
    {
        "id": 1,
        "name": "Descrição da transação",
        "value": -15.50,
        "date": "2024-01-15",
        "category": "Transporte",
        "categorization_confidence": 0.9,
        "categorization_reasoning": "Uber identificado no nome da transação"
    }
]
```

## Categorias Padrão

As seguintes categorias são usadas por padrão:

- **Alimentação**: Restaurantes, supermercados, delivery
- **Transporte**: Uber, táxi, gasolina, estacionamento
- **Saúde**: Farmácias, hospitais, médicos
- **Educação**: Cursos, livros, material escolar
- **Lazer**: Netflix, cinema, entretenimento
- **Casa/Utilidades**: Luz, água, gás, internet
- **Vestuário**: Roupas, sapatos, acessórios
- **Investimentos**: Aplicações, ações, fundos
- **Salário**: Rendimentos, pagamentos
- **Transferências**: PIX, TED, DOC
- **Impostos**: IPTU, IPVA, IR
- **Seguros**: Seguro de vida, carro, saúde
- **Outros**: Categorias não classificadas

## Configurações

### Modelo Gemini

Por padrão, usa o modelo `gemini-1.5-flash`. Para usar outros modelos:

```python
classifier = TransactionClassifier()
# O modelo é configurado internamente como 'gemini-1.5-flash'
```

### Parâmetros de Categorização

```python
from src.config.categories import CATEGORIZATION_CONFIG

# Configurações disponíveis
print(CATEGORIZATION_CONFIG)
# {
#     "model": "gpt-3.5-turbo",  # Será atualizado para gemini
#     "temperature": 0.1,
#     "max_tokens": 2000,
#     "timeout": 30,
#     "retry_attempts": 3,
#     "batch_size": 10
# }
```

## Tratamento de Erros

A integração inclui tratamento robusto de erros:

- **API Key não configurada**: Retorna transações com categoria "Outros"
- **Erro na API**: Retorna transações com categoria padrão
- **Resposta inválida**: Usa categorização de fallback
- **Timeout**: Retorna após timeout configurado

## Exemplo Prático

```python
# Transações de exemplo
transactions = [
    {"id": 1, "name": "Uber *uber.com.br", "value": -15.50, "date": "2024-01-15"},
    {"id": 2, "name": "Restaurante Sushi Bar", "value": -89.90, "date": "2024-01-14"},
    {"id": 3, "name": "Salário Janeiro", "value": 3500.00, "date": "2024-01-05"},
    {"id": 4, "name": "Farmácia São João", "value": -45.30, "date": "2024-01-12"},
    {"id": 5, "name": "Netflix", "value": -32.90, "date": "2024-01-10"}
]

result = categorize_with_gemini(transactions)

# Resultado esperado:
# Uber *uber.com.br → Transporte
# Restaurante Sushi Bar → Alimentação  
# Salário Janeiro → Salário
# Farmácia São João → Saúde
# Netflix → Lazer
```


## Limitações e Considerações

1. **Custo**: Cada chamada à API tem custo baseado em tokens
2. **Latência**: Depende da velocidade da API do Google
3. **Rate Limits**: Respeita os limites da API do Google
4. **Idioma**: Otimizado para português brasileiro
5. **Precisão**: Depende da qualidade das descrições das transações

## Troubleshooting

### Erro: "API key do Google não fornecida"
```bash
export GOOGLE_API_KEY="sua-chave-aqui"
```

### Erro: "Biblioteca 'google-generativeai' não instalada"
```bash
pip install google-generativeai>=0.3.0
```

### Categorizações inconsistentes
- Use `temperature=0.1` para maior consistência
- Verifique a qualidade das descrições das transações
- Considere usar categorias mais específicas

### Timeout nas requisições
- Reduza o número de transações por lote
- Aumente o timeout nas configurações
- Use modelo mais rápido (gemini-1.5-flash)
