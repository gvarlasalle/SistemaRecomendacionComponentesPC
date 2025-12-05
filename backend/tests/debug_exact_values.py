# backend/debug_exact_values.py
"""Debug de valores exactos"""

import sys
import json
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
    mb_features = test_mb.get('features', {})
    mb_ram_type_raw = mb_features.get('supported_ram_type', 'N/A')
    mb_ram_type_upper = str(mb_ram_type_raw).upper().strip()
    print(f"   supported_ram_type (raw): '{mb_ram_type_raw}' (tipo: {type(mb_ram_type_raw)})")
    print(f"   supported_ram_type (upper): '{mb_ram_type_upper}'")
    print(f"   Features completas: {json.dumps(mb_features, indent=2, ensure_ascii=False)}")
    
    # Obtener todas las RAM
    all_rams = [c for c in recommender.components if c['type'] == 'RAM']
    print(f"\nTotal RAM: {len(all_rams)}")
    
    print(f"\nPrimeras 10 RAM:")
    for i, ram in enumerate(all_rams[:10], 1):
        ram_features = ram.get('features', {})
        ram_type_raw = ram_features.get('ram_type', 'N/A')
        ram_type_upper = str(ram_type_raw).upper().strip()
        
        compatible = ram_type_upper == mb_ram_type_upper if ram_type_upper and mb_ram_type_upper else False
        
        print(f"\n  {i}. {ram['name'][:50]}")
        print(f"     ram_type (raw): '{ram_type_raw}' (tipo: {type(ram_type_raw)})")
        print(f"     ram_type (upper): '{ram_type_upper}'")
        print(f"     MB soporta: '{mb_ram_type_upper}'")
        print(f"     ¿Coinciden?: {ram_type_upper == mb_ram_type_upper}")
        print(f"     Compatible: {compatible}")

