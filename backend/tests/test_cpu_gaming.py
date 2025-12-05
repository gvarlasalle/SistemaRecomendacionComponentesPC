# backend/test_cpu_gaming.py
"""Prueba la selección de CPU para gaming"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from api.pc_builder_service import PCBuilderService
from api.recommendation_service import RecommendationService

print("\n" + "="*80)
print("🎮 PRUEBA: Selección de CPU para Gaming (2000 soles)")
print("="*80)

service = PCBuilderService()
recommender = RecommendationService()

# 1. Ver qué CPU se selecciona actualmente
print("\n1️⃣ Configuración generada:")
config = service.build_pc_configuration("Quiero una PC para jugar Valorant, tengo 2000 soles")

if config['configuration'].get('CPU'):
    current_cpu = config['configuration']['CPU']
    print(f"\n   CPU Seleccionado: {current_cpu['name']}")
    print(f"   Precio: S/ {current_cpu['price']}")
    print(f"   Rating: {current_cpu.get('predicted_rating', 'N/A')}")
    features = current_cpu.get('features', {})
    print(f"   Cores: {features.get('cores', 'N/A')}")
    print(f"   Socket: {features.get('socket', 'N/A')}")
    
    # Verificar si es de gama baja
    name = current_cpu['name'].upper()
    is_low_end = any(x in name for x in ['RYZEN 3', 'CORE I3', 'ATHLON', 'PENTIUM', 'CELERON'])
    is_mid_high = any(x in name for x in ['RYZEN 5', 'RYZEN 7', 'RYZEN 9', 'CORE I5', 'CORE I7', 'CORE I9'])
    
    if is_low_end:
        print(f"   ⚠️  PROBLEMA: CPU de gama baja seleccionado")
    elif is_mid_high:
        print(f"   ✅ OK: CPU de gama media/alta seleccionado")
    else:
        print(f"   ℹ️  CPU de gama desconocida")

# 2. Ver CPUs disponibles
print("\n2️⃣ CPUs disponibles para gaming (perfil gamer_mid):")
cpu_recs = recommender.recommend('gamer_mid', model_type='mf', top_k=50, component_type='CPU')

budget = 2000
allocated = budget * 0.25  # 25% para CPU = S/ 500

print(f"\n   Presupuesto asignado para CPU: S/ {allocated:.0f}")
print(f"\n   CPUs dentro del presupuesto (S/ {allocated:.0f}):")
affordable = [c for c in cpu_recs if c['price'] <= allocated]

for i, cpu in enumerate(affordable[:10], 1):
    name = cpu['name'].upper()
    is_low_end = any(x in name for x in ['RYZEN 3', 'CORE I3'])
    is_mid_high = any(x in name for x in ['RYZEN 5', 'RYZEN 7', 'CORE I5', 'CORE I7'])
    marker = "⭐" if is_mid_high else "⚠️" if is_low_end else "  "
    print(f"   {marker} {i:2d}. {cpu['name'][:55]}")
    print(f"      Precio: S/ {cpu['price']:6.0f} | Rating: {cpu['predicted_rating']:.2f}")

print(f"\n   CPUs con presupuesto extendido (hasta S/ 600 = 30%):")
extended = [c for c in cpu_recs if allocated < c['price'] <= budget * 0.30]

for i, cpu in enumerate(extended[:10], 1):
    name = cpu['name'].upper()
    is_mid_high = any(x in name for x in ['RYZEN 5', 'RYZEN 7', 'CORE I5', 'CORE I7'])
    marker = "⭐ MEJOR OPCIÓN" if is_mid_high else "  "
    print(f"   {marker} {i:2d}. {cpu['name'][:55]}")
    print(f"      Precio: S/ {cpu['price']:6.0f} | Rating: {cpu['predicted_rating']:.2f}")

print("\n" + "="*80)

