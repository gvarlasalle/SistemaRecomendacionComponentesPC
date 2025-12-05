# backend/api/conversational_evaluator.py
"""
Sistema de evaluación para modelos conversacionales
Evalúa precisión en extracción de presupuesto, casos de uso, etc.
"""

import json
from pathlib import Path
from typing import Dict, List
import sys

sys.path.append(str(Path(__file__).parent.parent))

from api.chat_parser import ChatParser
from api.chat_parser_spacy import ChatParserSpacy
from api.chat_parser_embedding import ChatParserEmbedding


class ConversationalEvaluator:
    """Evalúa y compara modelos conversacionales"""
    
    def __init__(self):
        # Casos de prueba con valores esperados
        self.test_cases = [
            {
                'message': 'Quiero una PC para jugar Valorant, tengo 2000 soles',
                'expected': {
                    'budget': 2000,
                    'use_cases': ['gaming'],
                    'games': ['valorant'],
                    'suggested_profile': 'gamer_mid'
                }
            },
            {
                'message': 'PC para programar Python y machine learning, presupuesto 1800 soles',
                'expected': {
                    'budget': 1800,
                    'use_cases': ['development'],
                    'software': ['python', 'machine learning'],
                    'suggested_profile': 'developer_mid'
                }
            },
            {
                'message': 'Computadora para diseño gráfico con Photoshop, 2500 soles',
                'expected': {
                    'budget': 2500,
                    'use_cases': ['design'],
                    'software': ['photoshop'],
                    'suggested_profile': 'designer_mid'
                }
            },
            {
                'message': 'PC básica para oficina, Excel y Word, 900 soles',
                'expected': {
                    'budget': 900,
                    'use_cases': ['office'],
                    'suggested_profile': 'office_budget'
                }
            },
            {
                'message': 'Gaming en calidad ultra, juegos AAA, 4000 soles',
                'expected': {
                    'budget': 4000,
                    'use_cases': ['gaming'],
                    'performance_level': 'high',
                    'suggested_profile': 'gamer_high'
                }
            },
            {
                'message': 'Quiero jugar Minecraft y hacer tareas, 1000 soles',
                'expected': {
                    'budget': 1000,
                    'use_cases': ['gaming'],
                    'games': ['minecraft'],
                    'suggested_profile': 'gamer_budget'
                }
            },
            {
                'message': 'Necesito una computadora para editar video con Premiere Pro, tengo 3000 soles',
                'expected': {
                    'budget': 3000,
                    'use_cases': ['video_editing'],
                    'software': ['premiere'],
                    'suggested_profile': 'designer_high'
                }
            },
            {
                'message': 'PC para desarrollo web con JavaScript y React, 1500 soles',
                'expected': {
                    'budget': 1500,
                    'use_cases': ['development'],
                    'software': ['javascript'],
                    'suggested_profile': 'developer_mid'
                }
            }
        ]
    
    def evaluate_parser(self, parser, parser_name: str) -> Dict:
        """Evalúa un parser conversacional"""
        print(f"\n📊 Evaluando parser: {parser_name}")
        
        budget_correct = 0
        use_case_correct = 0
        profile_correct = 0
        total = len(self.test_cases)
        
        budget_errors = []
        use_case_errors = []
        profile_errors = []
        
        for test_case in self.test_cases:
            message = test_case['message']
            expected = test_case['expected']
            
            # Parsear
            parsed = parser.parse(message)
            
            # Evaluar presupuesto
            if parsed.get('budget') == expected.get('budget'):
                budget_correct += 1
            else:
                budget_errors.append({
                    'message': message,
                    'expected': expected.get('budget'),
                    'got': parsed.get('budget')
                })
            
            # Evaluar casos de uso (al menos uno debe coincidir)
            expected_use_cases = set(expected.get('use_cases', []))
            parsed_use_cases = set(parsed.get('use_cases', []))
            if expected_use_cases and parsed_use_cases & expected_use_cases:
                use_case_correct += 1
            elif not expected_use_cases and not parsed_use_cases:
                use_case_correct += 1
            else:
                use_case_errors.append({
                    'message': message,
                    'expected': expected.get('use_cases'),
                    'got': parsed.get('use_cases')
                })
            
            # Evaluar perfil sugerido
            if parsed.get('suggested_profile') == expected.get('suggested_profile'):
                profile_correct += 1
            else:
                profile_errors.append({
                    'message': message,
                    'expected': expected.get('suggested_profile'),
                    'got': parsed.get('suggested_profile')
                })
        
        budget_accuracy = budget_correct / total
        use_case_accuracy = use_case_correct / total
        profile_accuracy = profile_correct / total
        
        # Accuracy general (promedio)
        overall_accuracy = (budget_accuracy + use_case_accuracy + profile_accuracy) / 3
        
        return {
            'parser_name': parser_name,
            'budget_accuracy': budget_accuracy,
            'use_case_accuracy': use_case_accuracy,
            'profile_accuracy': profile_accuracy,
            'overall_accuracy': overall_accuracy,
            'budget_errors': budget_errors,
            'use_case_errors': use_case_errors,
            'profile_errors': profile_errors
        }
    
    def compare_all_parsers(self) -> Dict:
        """Compara todos los parsers disponibles"""
        print("\n" + "="*60)
        print("🔬 COMPARACIÓN DE MODELOS CONVERSACIONALES")
        print("="*60)
        
        parsers = {
            'rule_based': ChatParser(),
            'spacy': ChatParserSpacy(),
            'embedding': ChatParserEmbedding()
        }
        
        results = {}
        
        for parser_name, parser in parsers.items():
            try:
                result = self.evaluate_parser(parser, parser_name)
                results[parser_name] = result
            except Exception as e:
                print(f"⚠️  Error evaluando {parser_name}: {e}")
                results[parser_name] = None
        
        # Imprimir resultados
        print("\n" + "="*60)
        print("📊 RESULTADOS DE EVALUACIÓN")
        print("="*60)
        
        for parser_name, result in results.items():
            if result:
                print(f"\n{parser_name.upper()}:")
                print(f"  Budget Accuracy:    {result['budget_accuracy']:.4f}")
                print(f"  Use Case Accuracy:  {result['use_case_accuracy']:.4f}")
                print(f"  Profile Accuracy:   {result['profile_accuracy']:.4f}")
                print(f"  Overall Accuracy:   {result['overall_accuracy']:.4f}")
        
        # Determinar mejor parser
        valid_results = {k: v for k, v in results.items() if v}
        if valid_results:
            best_parser = max(valid_results, key=lambda k: valid_results[k]['overall_accuracy'])
            
            print("\n" + "="*60)
            print(f"🏆 MEJOR PARSER: {best_parser.upper()}")
            print("="*60)
            
            return {
                'results': results,
                'best_parser': best_parser
            }
        
        return {'results': results, 'best_parser': None}


if __name__ == "__main__":
    evaluator = ConversationalEvaluator()
    comparison = evaluator.compare_all_parsers()
    
    # Guardar resultados
    output_path = Path(__file__).parent.parent / 'ml_models' / 'conversational_comparison_results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, default=str)
    
    print(f"\n💾 Resultados guardados en: {output_path}")

