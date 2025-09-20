"""
Classificador de transações usando Google Gemini
"""

import json
import os
from typing import List, Dict, Any, Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)


class TransactionClassifier:
    """Classificador de transações usando Google Gemini"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o classificador
        
        Args:
            api_key: Chave da API Google. Se não fornecida, usa GOOGLE_API_KEY do ambiente
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("API key do Google não fornecida. Configure GOOGLE_API_KEY no ambiente.")
        
        # Categorias padrão para transações financeiras
        self.default_categories = [
            "Alimentação",
            "Transporte",
            "Saúde",
            "Moradia",
            "Entretenimento",
            "Renda",
            "Receita",
            "Transferências",
            "Outros",
            "Estudo"
        ]
        
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa o cliente Gemini"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai
            logger.info("Cliente Gemini inicializado com sucesso")
        except ImportError:
            raise ImportError("Biblioteca 'google-generativeai' não instalada. Execute: pip install google-generativeai")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente Gemini: {e}")
            raise
    
    def categorize_transactions(self, transactions: List[Dict[str, Any]], 
                              custom_categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Categoriza uma lista de transações usando Gemini
        
        Args:
            transactions: Lista de transações no formato JSON
            custom_categories: Lista opcional de categorias personalizadas
            
        Returns:
            Lista de transações com categorias atribuídas
        """
        if not transactions:
            return []
        
        categories = custom_categories or self.default_categories
        
        try:
            # Prepara o prompt para o Gemini
            prompt = self._build_categorization_prompt(transactions, categories)
            
            # Chama a API do Gemini
            response = self._call_gemini_api(prompt)
            
            # Processa a resposta
            categorized_transactions = self._process_categorization_response(
                response, transactions
            )
            
            logger.info(f"Categorização concluída para {len(transactions)} transações")
            return categorized_transactions
            
        except Exception as e:
            logger.error(f"Erro na categorização: {e}")
            # Retorna transações sem categorização em caso de erro
            return [self._add_default_category(tx) for tx in transactions]
    
    def _build_categorization_prompt(self, transactions: List[Dict[str, Any]], 
                                   categories: List[str]) -> str:
        """Constrói o prompt para o Gemini"""
        
        # Formata as transações para o prompt
        transactions_text = ""
        for i, tx in enumerate(transactions, 1):
            transactions_text += f"{i}. {tx['name']} - R$ {tx['value']:.2f} ({tx['date']})\n"
        
        prompt = f"""
Você é um especialista em categorização de transações financeiras pessoais. 
Analise as seguintes transações e categorize cada uma usando APENAS as categorias fornecidas.

Categorias disponíveis: {', '.join(categories)}

Transações para categorizar:
{transactions_text}

IMPORTANTE:
- Responda APENAS no formato JSON válido
- Use apenas as categorias fornecidas
- Para cada transação, forneça a categoria mais adequada
- Se uma transação não se encaixar bem em nenhuma categoria, use "Outros"

Formato da resposta:
{{
    "categorizations": [
        {{"transaction_index": 1, "category": "Alimentação", "confidence": 0.9, "reasoning": "Restaurante identificado no nome"}},
        {{"transaction_index": 2, "category": "Transporte", "confidence": 0.8, "reasoning": "Uber identificado"}}
    ]
}}

Responda apenas com o JSON, sem texto adicional:
"""
        
        return prompt
    
    def _call_gemini_api(self, prompt: str) -> str:
        """Chama a API do Gemini"""
        try:
            model = self.client.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Erro ao chamar API do Gemini: {e}")
            raise
    
    def _process_categorization_response(self, response: str, 
                                       original_transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processa a resposta do Gemini e aplica as categorizações"""
        try:
            # Parse da resposta JSON
            result = json.loads(response)
            categorizations = result.get('categorizations', [])
            
            # Cria um mapa de categorizações por índice
            categorization_map = {}
            for cat in categorizations:
                idx = cat['transaction_index'] - 1  # Converte para índice baseado em 0
                if 0 <= idx < len(original_transactions):
                    categorization_map[idx] = cat
            
            # Aplica as categorizações
            categorized_transactions = []
            for i, tx in enumerate(original_transactions):
                tx_copy = tx.copy()
                
                if i in categorization_map:
                    cat_info = categorization_map[i]
                    tx_copy['category'] = cat_info['category']
                    tx_copy['categorization_confidence'] = cat_info.get('confidence', 0.5)
                    tx_copy['categorization_reasoning'] = cat_info.get('reasoning', '')
                else:
                    tx_copy['category'] = 'Outros'
                    tx_copy['categorization_confidence'] = 0.0
                    tx_copy['categorization_reasoning'] = 'Não foi possível categorizar'
                
                categorized_transactions.append(tx_copy)
            
            return categorized_transactions
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao processar resposta JSON do Gemini: {e}")
            logger.error(f"Resposta recebida: {response}")
            # Retorna transações sem categorização em caso de erro de parsing
            return [self._add_default_category(tx) for tx in original_transactions]
        except Exception as e:
            logger.error(f"Erro ao processar categorizações: {e}")
            return [self._add_default_category(tx) for tx in original_transactions]
    
    def _add_default_category(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Adiciona categoria padrão a uma transação"""
        tx_copy = transaction.copy()
        tx_copy['category'] = 'Outros'
        tx_copy['categorization_confidence'] = 0.0
        tx_copy['categorization_reasoning'] = 'Categorização automática falhou'
        return tx_copy


def categorize_with_gemini(transactions: List[Dict[str, Any]], 
                          api_key: Optional[str] = None,
                          custom_categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Função de conveniência para categorizar transações com Gemini
    
    Args:
        transactions: Lista de transações no formato JSON
        api_key: Chave da API Google (opcional)
        custom_categories: Lista de categorias personalizadas (opcional)
        
    Returns:
        Lista de transações categorizadas
    """
    classifier = TransactionClassifier(api_key)
    return classifier.categorize_transactions(transactions, custom_categories)
