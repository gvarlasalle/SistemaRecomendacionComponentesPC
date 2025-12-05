# backend/debug_ram_issue.py
"""Debug del problema de RAM DDR4"""

import sys
from pathlib import Path
import json
sys.path.append(str(Path(__file__).parent))

from api.pc_builder_service import PCBuilderService
from api.recommendation_service import RecommendationService

print("\n" + "="*60)
print("🔍 DEBUG: Problema RAM DDR4")
print("="*60)

service = PCBuilderService()
recommender = RecommendationService()

# 1. Ver todas las RAM disponibles
print("\n1️⃣ Todas las RAM disponibles en el dataset:")
all_rams = [c for c in recommender.components if c['type'] == 'RAM']
print(f"   Total de RAM: {len(all_rams)}")

ram_by_type = {}
for ram in all_rams:
    ram_type = ram.get('features', {}).get('ram_type', 'SIN_TIPO')
    if ram_type not in ram_by_type:
        ram_by_type[ram_type] = []
    ram_by_type[ram_type].append(ram)

print(f"\n   Por tipo:")
for ram_type, rams in sorted(ram_by_type.items()):
    print(f"      {ram_type}: {len(rams)} componentes")
    for ram in rams[:3]:  # Mostrar primeros 3
        print(f"         - {ram['name'][:50]} (S/ {ram['regular_price']})")

# 2. Ver motherboards DDR4
print("\n2️⃣ Motherboards que soportan DDR4:")
mb_ddr4 = [c for c in recommender.components 
           if c['type'] == 'MOTHERBOARD' 
           and c.get('features', {}).get('supported_ram_type', '').upper() == 'DDR4']
print(f"   Total: {len(mb_ddr4)}")
for mb in mb_ddr4[:5]:
    print(f"      - {mb['name'][:50]} (S/ {mb['regular_price']})")

# 3. Probar recomendación de RAM para developer_mid
print("\n3️⃣ Recomendaciones de RAM para developer_mid (modelo MF):")
ram_recs = recommender.recommend('developer_mid', model_type='mf', top_k=200, component_type='RAM')
print(f"   Total recomendadas: {len(ram_recs)}")
print(f"\n   Top 10 RAM recomendadas:")
for i, ram in enumerate(ram_recs[:10], 1):
    ram_type = ram.get('features', {}).get('ram_type', 'N/A')
    print(f"      {i}. {ram['name'][:45]} | Tipo: {ram_type} | Rating: {ram['predicted_rating']:.2f} | S/ {ram['price']}")

# 4. Simular selección de motherboard y ver qué RAM son compatibles
print("\n4️⃣ Simulando selección de motherboard DDR4 y filtrando RAM:")
# Usar una motherboard DDR4 común
test_mb = None
for mb in mb_ddr4:
    if mb['regular_price'] <= 300:
        test_mb = mb
        break

if test_mb:
    print(f"   Motherboard seleccionada: {test_mb['name'][:50]}")
    print(f"   Soporta RAM: {test_mb.get('features', {}).get('supported_ram_type', 'N/A')}")
    
    # Filtrar RAM compatibles
    selected_components = {'MOTHERBOARD': test_mb}
    compatible_rams = service.filter_compatible_components(ram_recs, selected_components, 'RAM')
    
    print(f"\n   RAM compatibles encontradas: {len(compatible_rams)}")
    if compatible_rams:
        print(f"   Top 5 RAM compatibles:")
        for i, ram in enumerate(compatible_rams[:5], 1):
            ram_type = ram.get('features', {}).get('ram_type', 'N/A')
            print(f"      {i}. {ram['name'][:45]} | Tipo: {ram_type} | S/ {ram['price']}")
    else:
        print(f"   ❌ PROBLEMA: No se encontraron RAM compatibles")
        print(f"\n   Verificando por qué...")
        for ram in ram_recs[:10]:
            ram_type = ram.get('features', {}).get('ram_type', '').upper()
            mb_ram_type = test_mb.get('features', {}).get('supported_ram_type', '').upper()
            print(f"      RAM: {ram_type} vs MB: {mb_ram_type} -> {'✅' if ram_type == mb_ram_type else '❌'}")

print("\n" + "="*60)

