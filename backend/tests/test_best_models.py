# backend/test_best_models.py
"""
Script de prueba para verificar que los mejores modelos se usan correctamente
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from config.model_config import get_best_models, get_recommendation_model, get_conversational_model
from api.pc_builder_service import PCBuilderService

print("\n" + "="*60)
print("🧪 PRUEBA DEL SISTEMA CON MEJORES MODELOS")
print("="*60)

# 1. Verificar configuración de modelos
print("\n1️⃣ Verificando configuración de modelos...")
best_models = get_best_models()
print(f"   ✅ Mejores modelos detectados:")
print(f"      - Recomendación: {best_models['recommendation_model']}")
print(f"      - Conversacional: {best_models['conversational_model']}")

rec_model = get_recommendation_model()
conv_model = get_conversational_model()
print(f"\n   ✅ Modelos a usar:")
print(f"      - Recomendación: {rec_model}")
print(f"      - Conversacional: {conv_model}")

# 2. Inicializar servicio
print("\n2️⃣ Inicializando PCBuilderService...")
service = PCBuilderService()
print(f"   ✅ Parser usado: {type(service.chat_parser).__name__}")
print(f"   ✅ Modelo por defecto: {service.default_model_type}")

# 3. Probar parsing
print("\n3️⃣ Probando parsing de mensaje...")
test_message = "Quiero una PC para jugar Valorant, tengo 2000 soles"
parsed = service.chat_parser.parse(test_message)
print(f"   ✅ Mensaje parseado:")
print(f"      - Presupuesto: S/ {parsed['budget']}")
print(f"      - Casos de uso: {parsed['use_cases']}")
print(f"      - Perfil sugerido: {parsed['suggested_profile']}")

# 4. Probar generación de configuración
print("\n4️⃣ Probando generación de configuración...")
print("   (Esto puede tardar unos segundos...)")
try:
    config = service.build_pc_configuration(test_message)
    
    print(f"\n   ✅ Configuración generada exitosamente!")
    print(f"      - Modelo usado: {config.get('model_used', 'N/A')}")
    print(f"      - Total: S/ {config['costs']['total']:.0f}")
    print(f"      - Presupuesto: S/ {config['costs']['budget']:.0f}")
    print(f"      - Diferencia: S/ {config['costs']['remaining']:.0f}")
    print(f"      - Uso del presupuesto: {config['costs']['compliance_percentage']:.1f}%")
    print(f"      - Dentro de presupuesto: {'✅ Sí' if config['costs']['within_budget'] else '❌ No'}")
    print(f"      - Compatibilidad válida: {'✅ Sí' if config['compatibility']['is_valid'] else '❌ No'}")
    
    if config['compatibility']['errors']:
        print(f"      - Errores de compatibilidad: {len(config['compatibility']['errors'])}")
        for error in config['compatibility']['errors']:
            print(f"        ❌ {error}")
    
    if config['compatibility']['warnings']:
        print(f"      - Advertencias: {len(config['compatibility']['warnings'])}")
        for warning in config['compatibility']['warnings']:
            print(f"        ⚠️  {warning}")
    
    # Mostrar componentes seleccionados
    print(f"\n   📦 Componentes seleccionados:")
    for comp_type, comp in config['configuration'].items():
        print(f"      - {comp_type}: {comp['name'][:40]} (S/ {comp['price']:.0f})")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# 5. Verificar que se usa el mejor modelo
print("\n5️⃣ Verificando que se usa el mejor modelo...")
if config.get('model_used') == rec_model:
    print(f"   ✅ Correcto: Se está usando el mejor modelo ({rec_model})")
else:
    print(f"   ⚠️  Se está usando {config.get('model_used')} en lugar de {rec_model}")

print("\n" + "="*60)
print("✅ PRUEBA COMPLETADA")
print("="*60 + "\n")

