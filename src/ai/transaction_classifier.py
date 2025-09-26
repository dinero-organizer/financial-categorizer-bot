"""
Classificador de transações usando Google Gemini

"""

import json
import re
import os
from typing import List, Dict, Any, Optional

from src.utils.logger import get_logger
from src.domain.categories import Category

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
        
        # Categorias padrão
        self.default_categories = [c.value for c in Category]
        
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
    
    def categorize_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Categoriza uma lista de transações usando Gemini
        
        Args:
            transactions: Lista de transações no formato JSON
        
        Returns:
            Lista de transações com categorias atribuídas
        """
        if not transactions:
            return []
        
        categories = self.default_categories
        logger.info(f"AI: iniciando categorização | transações={len(transactions)} | categorias={len(categories)}")
        
        try:
            # Prepara o prompt para o Gemini
            prompt = self._build_categorization_prompt(transactions, categories)
            logger.info(f"AI: prompt construído | tamanho={len(prompt)}")
            
            # Chama a API do Gemini
            response = self._call_gemini_api(prompt)
            logger.info(f"AI: resposta recebida da API | tamanho={len(response) if response else 0}")
            
            # Processa a resposta
            categorized_transactions = self._process_categorization_response(
                response, transactions
            )
            # Estatísticas de saída
            num_outros = sum(1 for tx in categorized_transactions if tx.get('category') == 'Outros')
            logger.info(f"AI: categorização concluída | total={len(transactions)} | outros={num_outros}")
            return categorized_transactions
            
        except Exception as e:
            logger.error(f"AI: erro na categorização: {e}")
            # Retorna transações sem categorização em caso de erro
            return [self._add_default_category(tx) for tx in transactions]
    
    def _build_categorization_prompt(self, transactions: List[Dict[str, Any]], 
                                   categories: List[str]) -> str:
        """Constrói o prompt para o Gemini"""
        
        # Formata as transações para o prompt
        transactions_text = ""
        for tx in transactions:
            transactions_text += f"ID: {tx['id']} | {tx['name']} - R$ {tx['value']:.2f} ({tx['date']})\n"
        
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
- Utilize o campo 'id' de cada transação para identificar no resultado
- Se uma transação não se encaixar bem em nenhuma categoria, use "Outros"
- NÃO use categorias de tipo de transação (ex.: "Transferências", "Receita")
- Classifique por finalidade/tema (ex.: alimentação, transporte, saúde etc.)
- Créditos (valor positivo) podem ser "Renda" (ex.: salário). Débitos (valor negativo) não podem ser "Renda"

Formato da resposta:
{{
    "categorizations": [
        {{"id": 123, "category": "Alimentação", "confidence": 0.9, "reasoning": "Restaurante identificado no nome"}},
        {{"id": 456, "category": "Transporte", "confidence": 0.8, "reasoning": "Uber identificado"}}
    ]
}}

Responda apenas com o JSON, sem texto adicional:
"""
        
        return prompt
    
    def _call_gemini_api(self, prompt: str) -> str:
        """Chama a API do Gemini"""
        try:
            # Usa um único modelo: override via GEMINI_MODEL_ID, senão padrão free-tier amigável
            model_name = os.getenv("GEMINI_MODEL_ID", "gemini-1.5-flash-8b").strip() or "gemini-1.5-flash-8b"
            logger.info(f"AI: usando modelo '{model_name}'")
            model = self.client.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = (response.text or "").strip()
            logger.info(f"AI: resposta do modelo '{model_name}' (completa):\n{text}")
            return text
            
        except Exception as e:
            logger.error(f"AI: erro ao chamar API do Gemini: {e}")
            raise
    
    def _process_categorization_response(self, response: str, 
                                       original_transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processa a resposta do Gemini e aplica as categorizações"""
        try:
            # Remove cercas de código markdown e extrai apenas o JSON
            logger.info(f"AI: iniciando parse da resposta | tamanho={len(response) if response else 0}")
            cleaned = self._extract_json_from_text(response)
            logger.info(f"AI: JSON extraído (completo):\n{cleaned}")
            # Parse da resposta JSON
            result = json.loads(cleaned)
            categorizations = result.get('categorizations', [])
            logger.info(f"AI: itens em 'categorizations' = {len(categorizations)}")
            
            # Cria um mapa de categorizações por id
            categorization_map = {}
            for cat in categorizations:
                tx_id = cat.get('id')
                if tx_id is not None:
                    categorization_map[tx_id] = cat
            
            # Aplica as categorizações
            categorized_transactions = []
            for tx in original_transactions:
                tx_copy = tx.copy()
                tx_id = tx.get('id')
                if tx_id in categorization_map:
                    cat_info = categorization_map[tx_id]
                    tx_copy['category'] = cat_info['category']
                    tx_copy['categorization_confidence'] = cat_info.get('confidence', 0.5)
                    tx_copy['categorization_reasoning'] = cat_info.get('reasoning', '')
                else:
                    tx_copy['category'] = 'Outros'
                    tx_copy['categorization_confidence'] = 0.0
                    tx_copy['categorization_reasoning'] = 'Não foi possível categorizar'
                categorized_transactions.append(tx_copy)
            
            logger.info(f"AI: mapeamento aplicado | categorizadas={len(categorized_transactions)}")
            return categorized_transactions
            
        except json.JSONDecodeError as e:
            logger.error(f"AI: erro JSONDecode ao processar resposta: {e}")
            logger.error(f"AI: resposta recebida (completa): {str(response)}")
            # Retorna transações sem categorização em caso de erro de parsing
            return [self._add_default_category(tx) for tx in original_transactions]
        except Exception as e:
            logger.error(f"AI: erro ao processar categorizações: {e}")
            return [self._add_default_category(tx) for tx in original_transactions]

    def _extract_json_from_text(self, text: str) -> str:
        """Extrai o bloco JSON de uma string possivelmente cercada por markdown.

        Aceita formatos como:
        ```json
        { ... }
        ```
        ou texto com JSON embutido. Se não encontrar, retorna o texto original.
        """
        if not text:
            return text
        text = text.strip()
        fence_pattern = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)
        match = fence_pattern.search(text)
        if match:
            return match.group(1).strip()
        # fallback: tenta recortar do primeiro '{' até o último '}'
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            return text[start:end+1].strip()
        return text
    
    def _add_default_category(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Adiciona categoria padrão a uma transação"""
        tx_copy = transaction.copy()
        tx_copy['category'] = 'Outros'
        tx_copy['categorization_confidence'] = 0.0
        tx_copy['categorization_reasoning'] = 'Categorização automática falhou'
        return tx_copy


def categorize_with_gemini(transactions: List[Dict[str, Any]], 
                          api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Função de conveniência para categorizar transações com Gemini
    
    Args:
        transactions: Lista de transações no formato JSON
        api_key: Chave da API Google (opcional)
    
    Returns:
        Lista de transações categorizadas
    """
    classifier = TransactionClassifier(api_key)
    return classifier.categorize_transactions(transactions)
