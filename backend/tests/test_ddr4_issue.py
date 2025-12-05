# backend/test_ddr4_issue.py
"""Prueba específica del problema DDR5 vs DDR4"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from api.pc_builder_service import PCBuilderService

print("\n" + "="*60)
print("🧪 PRUEBA: Problema DDR5 vs DDR4")
print("="*60)

service = PCBuilderService()

test_message = "PC para programar Python y machine learning, 1800 soles"
print(f"\nMensaje: {test_message}\n")

config = service.build_pc_configuration(test_message)

print("\n" + "="*60)
print("RESULTADO:")
print("="*60)

if 'RAM' in config['configuration']:
    ram = config['configuration']['RAM']
    ram_type = ram.get('features', {}).get('ram_type', 'N/A')
    print(f"✅ RAM seleccionada: {ram['name'][:50]}")
    print(f"   Tipo de RAM: {ram_type}")
    
    if 'MOTHERBOARD' in config['configuration']:
        mb = config['configuration']['MOTHERBOARD']
        mb_ram_type = mb.get('features', {}).get('supported_ram_type', 'N/A')
        print(f"   Motherboard soporta: {mb_ram_type}")
        
        if ram_type.upper() == mb_ram_type.upper():
            print(f"\n✅ PERFECTO: RAM {ram_type} es compatible con Motherboard {mb_ram_type}")
        else:
            print(f"\n❌ ERROR: RAM {ram_type} NO es compatible con Motherboard {mb_ram_type}")
else:
    print("❌ RAM no fue seleccionada")

print(f"\nCompatibilidad válida: {'✅ SÍ' if config['compatibility']['is_valid'] else '❌ NO'}")

if not config['compatibility']['is_valid']:
    print("\n❌ ERRORES DE COMPATIBILIDAD:")
    for error in config['compatibility']['errors']:
        print(f"   - {error}")

print("\n" + "="*60)

