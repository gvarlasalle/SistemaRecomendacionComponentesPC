# backend/test_simple.py
"""Prueba simple del sistema"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from api.pc_builder_service import PCBuilderService

print("\n" + "="*60)
print("🧪 PRUEBA SIMPLE DEL SISTEMA")
print("="*60)

service = PCBuilderService()

# Prueba con diferentes casos
test_cases = [
    "PC para oficina, Excel y Word, 900 soles",
    "PC para programar Python, 1500 soles"
]

for i, message in enumerate(test_cases, 1):
    print(f"\n{'='*60}")
    print(f"Prueba {i}: {message}")
    print("="*60)
    
    try:
        config = service.build_pc_configuration(message)
        
        print(f"\n✅ Resultado:")
        print(f"   Modelo usado: {config.get('model_used', 'N/A')}")
        print(f"   Total: S/ {config['costs']['total']:.0f}")
        print(f"   Presupuesto: S/ {config['costs']['budget']:.0f}")
        print(f"   Dentro de presupuesto: {'✅' if config['costs']['within_budget'] else '❌'}")
        print(f"   Compatible: {'✅' if config['compatibility']['is_valid'] else '❌'}")
        
        if not config['compatibility']['is_valid']:
            print(f"   Errores: {len(config['compatibility']['errors'])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "="*60)
print("✅ PRUEBAS COMPLETADAS")
print("="*60 + "\n")

