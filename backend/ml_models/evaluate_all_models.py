# backend/evaluate_all_models.py
"""
Script principal para evaluar y comparar todos los modelos
Ejecuta evaluación de modelos de recomendación y conversacionales
"""

import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

from ml_models.model_evaluator import ModelEvaluator
from api.conversational_evaluator import ConversationalEvaluator


def main():
    """Función principal de evaluación"""
    
    print("\n" + "="*80)
    print("🔬 EVALUACIÓN COMPLETA DE MODELOS")
    print("="*80)
    
    # 1. Evaluar modelos de recomendación (filtrado colaborativo)
    print("\n" + "="*80)
    print("📊 EVALUANDO MODELOS DE FILTRADO COLABORATIVO")
    print("="*80)
    
    rec_evaluator = ModelEvaluator()
    rec_results = rec_evaluator.compare_all_models()
    
    # 2. Evaluar modelos conversacionales
    print("\n" + "="*80)
    print("💬 EVALUANDO MODELOS CONVERSACIONALES")
    print("="*80)
    
    conv_evaluator = ConversationalEvaluator()
    conv_results = conv_evaluator.compare_all_parsers()
    
    # 3. Resumen final
    print("\n" + "="*80)
    print("📋 RESUMEN FINAL")
    print("="*80)
    
    print("\n🏆 MEJOR MODELO DE RECOMENDACIÓN:")
    if rec_results.get('best_model'):
        best_rec = rec_results['best_model']
        print(f"   {best_rec.upper()}")
        if best_rec in rec_results['results']:
            result = rec_results['results'][best_rec]
            print(f"   RMSE: {result['rating_metrics']['rmse']:.4f}")
            print(f"   MAE:  {result['rating_metrics']['mae']:.4f}")
            print(f"   NDCG@10: {result['ranking_metrics']['ndcg@k']:.4f}")
    else:
        print("   No se pudo determinar")
    
    print("\n🏆 MEJOR MODELO CONVERSACIONAL:")
    if conv_results.get('best_parser'):
        best_conv = conv_results['best_parser']
        print(f"   {best_conv.upper()}")
        if best_conv in conv_results['results'] and conv_results['results'][best_conv]:
            result = conv_results['results'][best_conv]
            print(f"   Overall Accuracy: {result['overall_accuracy']:.4f}")
            print(f"   Budget Accuracy:  {result['budget_accuracy']:.4f}")
            print(f"   Use Case Accuracy: {result['use_case_accuracy']:.4f}")
    else:
        print("   No se pudo determinar")
    
    # 4. Guardar resultados completos
    output_dir = Path(__file__).parent / 'ml_models'
    output_dir.mkdir(exist_ok=True)
    
    all_results = {
        'recommendation_models': rec_results,
        'conversational_models': conv_results,
        'recommendations': {
            'best_recommendation_model': rec_results.get('best_model'),
            'best_conversational_model': conv_results.get('best_parser')
        }
    }
    
    output_path = output_dir / 'complete_evaluation_results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n💾 Resultados completos guardados en: {output_path}")
    
    # 5. Actualizar archivo de configuración de mejores modelos
    config_dir = Path(__file__).parent / 'config'
    config_dir.mkdir(exist_ok=True)
    config_path = config_dir / 'best_models.json'
    
    from datetime import datetime
    config_data = {
        'recommendation_model': rec_results.get('best_model', 'rule'),
        'conversational_model': conv_results.get('best_parser', 'rule_based'),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'notes': 'Mejores modelos determinados por evaluación automática. Actualizar ejecutando evaluate_all_models.py'
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2)
    
    print(f"💾 Configuración de mejores modelos actualizada en: {config_path}")
    
    # 5. Recomendaciones de uso
    print("\n" + "="*80)
    print("💡 RECOMENDACIONES DE USO")
    print("="*80)
    
    print("\nPara usar los mejores modelos en producción:")
    print(f"   - Modelo de recomendación: '{rec_results.get('best_model', 'rule')}'")
    print(f"   - Modelo conversacional: '{conv_results.get('best_parser', 'rule_based')}'")
    print("\nEjemplo de uso en código:")
    print(f"   service = PCBuilderService(parser_type='{conv_results.get('best_parser', 'rule_based').replace('_', '')}')")
    print(f"   config = service.build_pc_configuration(message, model_type='{rec_results.get('best_model', 'rule')}')")
    
    print("\n" + "="*80)
    print("✅ EVALUACIÓN COMPLETA FINALIZADA")
    print("="*80 + "\n")
    
    return all_results


if __name__ == "__main__":
    main()

