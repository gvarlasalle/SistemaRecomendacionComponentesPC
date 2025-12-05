# backend/test_cpu_final.py
"""Prueba final de selección de CPU para gaming"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from api.pc_builder_service import PCBuilderService

print("\n" + "="*70)
print("🎮 PRUEBA FINAL: CPU para Gaming (2000 soles)")
print("="*70)

service = PCBuilderService()

# Generar configuración
config = service.build_pc_configuration("Quiero una PC para jugar Valorant, tengo 2000 soles")

# Analizar CPU seleccionado
if config['configuration'].get('CPU'):
    cpu = config['configuration']['CPU']
    name = cpu['name'].upper()
    
    print(f"\n✅ CPU SELECCIONADO:")
    print(f"   Nombre: {cpu['name']}")
    print(f"   Precio: S/ {cpu['price']}")
    print(f"   Rating: {cpu.get('predicted_rating', 'N/A')}")
    
    # Verificar gama
    is_low_end = any(x in name for x in ['RYZEN 3', 'CORE I3', 'ATHLON', 'PENTIUM', 'CELERON'])
    is_mid_high = any(x in name for x in ['RYZEN 5', 'RYZEN 7', 'RYZEN 9', 'CORE I5', 'CORE I7', 'CORE I9'])
    
    print(f"\n📊 ANÁLISIS:")
    if is_low_end:
        print(f"   ⚠️  PROBLEMA: CPU de gama baja (Ryzen 3/Core i3)")
        print(f"   ❌ El sistema debería seleccionar Ryzen 5 o Core i5 para gaming")
    elif is_mid_high:
        print(f"   ✅ CORRECTO: CPU de gama media/alta seleccionado")
        print(f"   ✅ Adecuado para gaming")
    else:
        print(f"   ℹ️  CPU de gama desconocida")
    
    print(f"\n💰 Presupuesto:")
    print(f"   Total: S/ {config['costs']['total']:.0f}")
    print(f"   Presupuesto: S/ {config['costs']['budget']:.0f}")
    print(f"   Exceso: {config['costs']['compliance_percentage']:.1f}%")
else:
    print("\n❌ CPU no seleccionado")

print("\n" + "="*70)

