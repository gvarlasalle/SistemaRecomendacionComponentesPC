# backend/test_compatibility.py
"""Prueba específica de compatibilidad"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from api.pc_builder_service import PCBuilderService

print("\n" + "="*60)
print("🧪 PRUEBA DE COMPATIBILIDAD ESTRICTA")
print("="*60)

service = PCBuilderService()

test_message = "Quiero una PC para jugar Valorant, tengo 2000 soles"

print(f"\nMensaje: {test_message}")
print("\nGenerando configuración...\n")

config = service.build_pc_configuration(test_message)

print("\n" + "="*60)
print("RESULTADO:")
print("="*60)
print(f"Compatibilidad válida: {'✅ SÍ' if config['compatibility']['is_valid'] else '❌ NO'}")

if not config['compatibility']['is_valid']:
    print("\n❌ ERRORES DE COMPATIBILIDAD ENCONTRADOS:")
    for error in config['compatibility']['errors']:
        print(f"   - {error}")
    print("\n⚠️  ESTO NO DEBERÍA PASAR - El sistema debe garantizar compatibilidad")
else:
    print("\n✅ ¡Perfecto! Todos los componentes son compatibles")

print("\n" + "="*60)

