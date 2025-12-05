# backend/test_specific_cases.py
"""Prueba los casos específicos solicitados"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from api.pc_builder_service import PCBuilderService

service = PCBuilderService()

# Caso 1: Gaming - Valorant
print("\n" + "="*70)
print("CASO 1: Gaming - Valorant, 2000 soles")
print("="*70)
config1 = service.build_pc_configuration("Quiero una PC para jugar Valorant, tengo 2000 soles")

print("\n📊 ANÁLISIS:")
if config1['configuration']:
    total = config1['costs']['total']
    budget = config1['costs']['budget']
    print(f"Presupuesto: S/ {budget} | Usado: S/ {total:.0f} ({config1['costs']['compliance_percentage']:.1f}%)")
    
    gpu = config1['configuration'].get('GPU')
    cpu = config1['configuration'].get('CPU')
    if gpu:
        gpu_pct = (gpu['price'] / budget * 100)
        print(f"GPU: S/ {gpu['price']:.0f} ({gpu_pct:.1f}%) - {'✅' if 30 <= gpu_pct <= 50 else '⚠️'}")
    if cpu:
        cpu_pct = (cpu['price'] / budget * 100)
        print(f"CPU: S/ {cpu['price']:.0f} ({cpu_pct:.1f}%) - {'✅' if 20 <= cpu_pct <= 35 else '⚠️'}")

# Caso 2: Oficina básica
print("\n" + "="*70)
print("CASO 2: Oficina básica, 900 soles")
print("="*70)
config2 = service.build_pc_configuration("PC básica para oficina, Excel y Word, 900 soles")

print("\n📊 ANÁLISIS:")
if config2['configuration']:
    total = config2['costs']['total']
    budget = config2['costs']['budget']
    print(f"Presupuesto: S/ {budget} | Usado: S/ {total:.0f} ({config2['costs']['compliance_percentage']:.1f}%)")
    
    for comp_type, comp in config2['configuration'].items():
        pct = (comp['price'] / budget * 100)
        print(f"{comp_type:12s}: S/ {comp['price']:.0f} ({pct:5.1f}%)")

print("\n" + "="*70)

