# backend/analyze_cpu_selection.py
"""Analiza la selección de CPU para gaming"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from api.pc_builder_service import PCBuilderService
from api.recommendation_service import RecommendationService

print("\n" + "="*80)
print("🔍 ANÁLISIS: Selección de CPU para Gaming (2000 soles)")
print("="*80)

service = PCBuilderService()
recommender = RecommendationService()

# Simular la selección actual
print("\n1️⃣ Configuración actual generada:")
config = service.build_pc_configuration("Quiero una PC para jugar Valorant, tengo 2000 soles")

if config['configuration'].get('CPU'):
    current_cpu = config['configuration']['CPU']
    print(f"\n   CPU Seleccionado: {current_cpu['name']}")
    print(f"   Precio: S/ {current_cpu['price']}")
    print(f"   Rating: {current_cpu.get('predicted_rating', 'N/A')}")
    features = current_cpu.get('features', {})
    print(f"   Cores: {features.get('cores', 'N/A')}")
    print(f"   Socket: {features.get('socket', 'N/A')}")

# Ver todas las CPUs disponibles para gaming
print("\n2️⃣ CPUs disponibles para perfil 'gamer_mid':")
cpu_recommendations = recommender.recommend('gamer_mid', model_type='mf', top_k=50, component_type='CPU')

print(f"\n   Total CPUs recomendadas: {len(cpu_recommendations)}")
print(f"\n   Top 15 CPUs (ordenadas por rating):")
for i, cpu in enumerate(cpu_recommendations[:15], 1):
    cores = cpu.get('features', {}).get('cores', 0)
    socket = cpu.get('features', {}).get('socket', 'N/A')
    cpu_name = cpu['name']
    is_ryzen5_or_better = 'Ryzen 5' in cpu_name or 'Ryzen 7' in cpu_name or 'Ryzen 9' in cpu_name
    is_i5_or_better = 'Core i5' in cpu_name or 'Core i7' in cpu_name or 'Core i9' in cpu_name
    marker = "⭐" if (is_ryzen5_or_better or is_i5_or_better) else "  "
    print(f"   {marker} {i:2d}. {cpu_name[:50]}")
    print(f"      Precio: S/ {cpu['price']:6.0f} | Rating: {cpu['predicted_rating']:.2f} | Cores: {cores} | Socket: {socket}")

# Ver CPUs dentro del presupuesto asignado para gaming (25% = S/ 500)
print("\n3️⃣ CPUs dentro del presupuesto asignado (S/ 500 = 25% de 2000):")
budget = 2000
allocated = budget * 0.25  # 25% para CPU en gaming
print(f"   Presupuesto asignado para CPU: S/ {allocated:.0f}")

affordable_cpus = [c for c in cpu_recommendations if c['price'] <= allocated]
print(f"   CPUs dentro del presupuesto: {len(affordable_cpus)}")

if affordable_cpus:
    print(f"\n   CPUs asequibles (ordenadas por rating):")
    for i, cpu in enumerate(affordable_cpus[:10], 1):
        cores = cpu.get('features', {}).get('cores', 0)
        cpu_name = cpu['name']
        is_ryzen5_or_better = 'Ryzen 5' in cpu_name or 'Ryzen 7' in cpu_name
        is_i5_or_better = 'Core i5' in cpu_name or 'Core i7' in cpu_name
        marker = "⭐ RECOMENDADO" if (is_ryzen5_or_better or is_i5_or_better) else ""
        print(f"   {i:2d}. {cpu_name[:50]}")
        print(f"      Precio: S/ {cpu['price']:6.0f} | Rating: {cpu['predicted_rating']:.2f} | Cores: {cores} {marker}")

# Ver CPUs con un poco más de presupuesto (hasta S/ 600 = 30%)
print("\n4️⃣ CPUs con presupuesto extendido (hasta S/ 600 = 30%):")
extended_budget = budget * 0.30
extended_cpus = [c for c in cpu_recommendations if c['price'] <= extended_budget and c['price'] > allocated]
print(f"   CPUs entre S/ {allocated:.0f} y S/ {extended_budget:.0f}: {len(extended_cpus)}")

if extended_cpus:
    print(f"\n   CPUs en rango extendido (ordenadas por rating):")
    for i, cpu in enumerate(extended_cpus[:10], 1):
        cores = cpu.get('features', {}).get('cores', 0)
        cpu_name = cpu['name']
        is_ryzen5_or_better = 'Ryzen 5' in cpu_name or 'Ryzen 7' in cpu_name
        is_i5_or_better = 'Core i5' in cpu_name or 'Core i7' in cpu_name
        marker = "⭐ MEJOR OPCIÓN" if (is_ryzen5_or_better or is_i5_or_better) else ""
        print(f"   {i:2d}. {cpu_name[:50]}")
        print(f"      Precio: S/ {cpu['price']:6.0f} | Rating: {cpu['predicted_rating']:.2f} | Cores: {cores} {marker}")

print("\n" + "="*80)

