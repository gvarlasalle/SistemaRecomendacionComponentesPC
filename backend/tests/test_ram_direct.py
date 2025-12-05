# backend/test_ram_direct.py
"""Test directo del problema"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from api.recommendation_service import RecommendationService
from api.pc_builder_service import PCBuilderService

recommender = RecommendationService()
service = PCBuilderService()

# Obtener motherboard DDR4 directamente
mb_ddr4 = [c for c in recommender.components 
           if c['type'] == 'MOTHERBOARD' 
           and c.get('features', {}).get('supported_ram_type', '').upper() == 'DDR4']

if mb_ddr4:
    test_mb_raw = mb_ddr4[0]
    
    # Convertir a formato de recomendación (como lo hace el servicio)
    test_mb = {
        'component_id': test_mb_raw['id'],
        'name': test_mb_raw['name'],
        'type': test_mb_raw['type'],
        'price': test_mb_raw['regular_price'],
        'predicted_rating': 3.0,
        'features': test_mb_raw.get('features', {})
    }
    
    print(f"Motherboard: {test_mb['name']}")
    print(f"   Soporta: {test_mb['features'].get('supported_ram_type', 'N/A')}")
    
    # Obtener RAMs en formato de recomendación
    all_rams_raw = [c for c in recommender.components if c['type'] == 'RAM']
    ram_candidates = []
    
    for ram_raw in all_rams_raw:
        ram_candidates.append({
            'component_id': ram_raw['id'],
            'name': ram_raw['name'],
            'type': ram_raw['type'],
            'price': ram_raw['regular_price'],
            'predicted_rating': 3.0,
            'features': ram_raw.get('features', {})
        })
    
    print(f"\nTotal RAM candidatos: {len(ram_candidates)}")
    
    # Filtrar
    selected = {'MOTHERBOARD': test_mb}
    compatible = service.filter_compatible_components(ram_candidates, selected, 'RAM')
    
    print(f"\nRAM compatibles encontradas: {len(compatible)}")
    
    if compatible:
        print(f"\nTop 5 RAM compatibles:")
        for i, ram in enumerate(compatible[:5], 1):
            ram_type = ram.get('features', {}).get('ram_type', 'N/A')
            print(f"   {i}. {ram['name'][:50]}")
            print(f"      Tipo: {ram_type} | Precio: S/ {ram['price']}")
    else:
        print(f"\n❌ PROBLEMA: No se encontraron RAM compatibles")
        print(f"\nVerificando valores exactos:")
        mb_ram_type = test_mb['features'].get('supported_ram_type', '')
        print(f"   MB soporta: '{mb_ram_type}' (tipo: {type(mb_ram_type)})")
        
        for ram in ram_candidates[:5]:
            ram_type = ram.get('features', {}).get('ram_type', '')
            print(f"   RAM: '{ram_type}' (tipo: {type(ram_type)})")
            print(f"      Comparación: '{str(ram_type).upper().strip()}' vs '{str(mb_ram_type).upper().strip()}'")
            print(f"      ¿Coinciden?: {str(ram_type).upper().strip() == str(mb_ram_type).upper().strip()}")

