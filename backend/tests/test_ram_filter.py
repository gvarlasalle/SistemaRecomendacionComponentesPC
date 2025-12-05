# backend/test_ram_filter.py
"""Test del filtro de RAM"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from api.pc_builder_service import PCBuilderService
from api.recommendation_service import RecommendationService

service = PCBuilderService()
recommender = RecommendationService()

# Obtener una motherboard DDR4
mb_ddr4 = [c for c in recommender.components 
           if c['type'] == 'MOTHERBOARD' 
           and 'DDR4' in c.get('features', {}).get('supported_ram_type', '').upper()]

if mb_ddr4:
    test_mb = mb_ddr4[0]
    print(f"Motherboard: {test_mb['name']}")
    print(f"Soporta: {test_mb.get('features', {}).get('supported_ram_type', 'N/A')}")
    
    # Obtener todas las RAM
    all_rams = [c for c in recommender.components if c['type'] == 'RAM']
    print(f"\nTotal RAM: {len(all_rams)}")
    
    # Convertir a formato de recomendación
    ram_candidates = []
    for ram in all_rams:
        ram_candidates.append({
            'component_id': ram['id'],
            'name': ram['name'],
            'type': ram['type'],
            'price': ram['regular_price'],
            'predicted_rating': 3.0,
            'features': ram.get('features', {})
        })
    
    # Filtrar
    selected = {'MOTHERBOARD': test_mb}
    compatible = service.filter_compatible_components(ram_candidates, selected, 'RAM')
    
    print(f"\nRAM compatibles: {len(compatible)}")
    for ram in compatible[:5]:
        print(f"  - {ram['name'][:50]} | Tipo: {ram.get('features', {}).get('ram_type', 'N/A')}")

