# backend/config/model_config.py
"""
Configuración de modelos - Lee y gestiona los mejores modelos
"""

import json
from pathlib import Path
from typing import Dict, Optional


def get_best_models() -> Dict[str, str]:
    """
    Obtiene los mejores modelos desde el archivo de evaluación
    
    Returns:
        Dict con 'recommendation_model' y 'conversational_model'
    """
    # Intentar leer desde archivo de evaluación completo
    eval_file = Path(__file__).parent.parent / 'ml_models' / 'complete_evaluation_results.json'
    
    if eval_file.exists():
        try:
            with open(eval_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            best_rec = results.get('recommendations', {}).get('best_recommendation_model', 'rule')
            best_conv = results.get('recommendations', {}).get('best_conversational_model', 'rule_based')
            
            return {
                'recommendation_model': best_rec,
                'conversational_model': best_conv
            }
        except Exception as e:
            print(f"⚠️  Error leyendo evaluación: {e}")
    
    # Fallback: valores por defecto basados en evaluación reciente
    return {
        'recommendation_model': 'mf',  # Mejor según evaluación
        'conversational_model': 'rule_based'  # Mejor según evaluación
    }


def get_recommendation_model() -> str:
    """Obtiene el mejor modelo de recomendación"""
    return get_best_models()['recommendation_model']


def get_conversational_model() -> str:
    """Obtiene el mejor modelo conversacional"""
    conv_model = get_best_models()['conversational_model']
    # Convertir 'rule_based' a 'rule' para compatibilidad
    if conv_model == 'rule_based':
        return 'rule'
    return conv_model

