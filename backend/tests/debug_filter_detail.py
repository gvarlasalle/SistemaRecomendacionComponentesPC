# backend/debug_filter_detail.py
"""Debug detallado del filtro"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from api.recommendation_service import RecommendationService

recommender = RecommendationService()

# Obtener motherboard DDR4
mb_ddr4 = [c for c in recommender.components 
           if c['type'] == 'MOTHERBOARD' 
           and 'DDR4' in str(c.get('features', {}).get('supported_ram_type', '')).upper()]

if mb_ddr4:
    test_mb = mb_ddr4[0]
    print(f"Motherboard: {test_mb['name']}")
    print(f"Features completas: {json.dumps(test_mb.get('features', {}), indent=2)}")
    
    # Obtener todas las RAM
    all_rams = [c for c in recommender.components if c['type'] == 'RAM']
    print(f"\nTotal RAM: {len(all_rams)}")
    
    print(f"\nRAM disponibles:")
    for i, ram in enumerate(all_rams[:10], 1):
        ram_type = ram.get('features', {}).get('ram_type', 'SIN_TIPO')
        mb_ram_type = test_mb.get('features', {}).get('supported_ram_type', 'SIN_TIPO')
        
        ram_type_upper = str(ram_type).upper().strip()
        mb_ram_type_upper = str(mb_ram_type).upper().strip()
        
        compatible = ram_type_upper == mb_ram_type_upper if ram_type_upper and mb_ram_type_upper else False
        
        print(f"  {i}. {ram['name'][:50]}")
        print(f"     RAM tipo: '{ram_type}' -> '{ram_type_upper}'")
        print(f"     MB soporta: '{mb_ram_type}' -> '{mb_ram_type_upper}'")
        print(f"     Compatible: {compatible}")
        print(f"     Features: {ram.get('features', {})}")
        print()

