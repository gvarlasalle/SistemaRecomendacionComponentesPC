# backend/test_ram_compatibility.py
"""Prueba específica del problema de RAM DDR5 vs DDR4"""

import sys
from pathlib import Path
import json
sys.path.append(str(Path(__file__).parent))

from api.pc_builder_service import PCBuilderService
from api.recommendation_service import RecommendationService

print("\n" + "="*60)
print("🧪 PRUEBA ESPECÍFICA: RAM DDR5 vs DDR4")
print("="*60)

service = PCBuilderService()
recommender = RecommendationService()

# Verificar qué tipos de RAM hay disponibles
print("\n1️⃣ Verificando tipos de RAM en el dataset...")
all_components = recommender.components
ram_components = [c for c in all_components if c['type'] == 'RAM']
ram_types = {}
for ram in ram_components:
    ram_type = ram.get('features', {}).get('ram_type', 'UNKNOWN')
    if ram_type not in ram_types:
        ram_types[ram_type] = 0
    ram_types[ram_type] += 1

print(f"   Tipos de RAM disponibles:")
for ram_type, count in sorted(ram_types.items()):
    print(f"      - {ram_type}: {count} componentes")

# Verificar qué tipos de motherboard hay
print("\n2️⃣ Verificando tipos de motherboard en el dataset...")
mb_components = [c for c in all_components if c['type'] == 'MOTHERBOARD']
mb_ram_types = {}
for mb in mb_components:
    mb_ram_type = mb.get('features', {}).get('supported_ram_type', 'UNKNOWN')
    if mb_ram_type not in mb_ram_types:
        mb_ram_types[mb_ram_type] = 0
    mb_ram_types[mb_ram_type] += 1

print(f"   Tipos de RAM soportados por motherboards:")
for mb_ram_type, count in sorted(mb_ram_types.items()):
    print(f"      - {mb_ram_type}: {count} motherboards")

# Probar el caso específico
print("\n3️⃣ Probando caso específico del usuario...")
test_message = "PC para programar Python y machine learning, 1800 soles"
print(f"   Mensaje: {test_message}\n")

config = service.build_pc_configuration(test_message)

print("\n" + "="*60)
print("RESULTADO:")
print("="*60)

if 'MOTHERBOARD' in config['configuration']:
    mb = config['configuration']['MOTHERBOARD']
    mb_ram_type = mb.get('features', {}).get('supported_ram_type', 'N/A')
    print(f"Motherboard seleccionada: {mb['name'][:50]}")
    print(f"   RAM soportada: {mb_ram_type}")

if 'RAM' in config['configuration']:
    ram = config['configuration']['RAM']
    ram_type = ram.get('features', {}).get('ram_type', 'N/A')
    print(f"\nRAM seleccionada: {ram['name'][:50]}")
    print(f"   Tipo de RAM: {ram_type}")
    
    if 'MOTHERBOARD' in config['configuration']:
        mb_ram_type = config['configuration']['MOTHERBOARD'].get('features', {}).get('supported_ram_type', '')
        if ram_type.upper() != mb_ram_type.upper() and ram_type != 'N/A' and mb_ram_type:
            print(f"\n❌ ERROR: RAM {ram_type} ≠ Motherboard {mb_ram_type}")
        else:
            print(f"\n✅ Compatible: RAM {ram_type} = Motherboard {mb_ram_type}")
else:
    print("\n⚠️  RAM no fue seleccionada")

print(f"\nCompatibilidad válida: {'✅ SÍ' if config['compatibility']['is_valid'] else '❌ NO'}")

if not config['compatibility']['is_valid']:
    print("\n❌ ERRORES DE COMPATIBILIDAD:")
    for error in config['compatibility']['errors']:
        print(f"   - {error}")

print("\n" + "="*60)

