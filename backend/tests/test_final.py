# backend/test_final.py
"""Prueba final simplificada"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

# Suprimir prints durante la ejecución
import os
import sys
from io import StringIO

class SuppressOutput:
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = StringIO()
        return self
    def __exit__(self, *args):
        sys.stdout = self._stdout

from api.pc_builder_service import PCBuilderService

print("Inicializando servicio...")
with SuppressOutput():
    service = PCBuilderService()

print("\n" + "="*70)
print("CASO 1: Gaming - Valorant, 2000 soles")
print("="*70)

with SuppressOutput():
    config1 = service.build_pc_configuration("Quiero una PC para jugar Valorant, tengo 2000 soles")

if config1['configuration']:
    total = config1['costs']['total']
    budget = config1['costs']['budget']
    print(f"\n💰 Presupuesto: S/ {budget} | Usado: S/ {total:.0f} ({config1['costs']['compliance_percentage']:.1f}%)")
    print(f"   {'✅ Dentro de presupuesto' if config1['costs']['within_budget'] else '⚠️ Excede presupuesto'}")
    
    print(f"\n📦 Componentes:")
    for comp_type, comp in sorted(config1['configuration'].items()):
        pct = (comp['price'] / budget * 100)
        print(f"   {comp_type:12s}: S/ {comp['price']:6.0f} ({pct:5.1f}%)")
    
    gpu = config1['configuration'].get('GPU')
    cpu = config1['configuration'].get('CPU')
    if gpu:
        gpu_pct = (gpu['price'] / budget * 100)
        print(f"\n🎮 GPU: S/ {gpu['price']:.0f} ({gpu_pct:.1f}%) - {'✅' if 30 <= gpu_pct <= 50 else '⚠️'}")
    if cpu:
        cpu_pct = (cpu['price'] / budget * 100)
        print(f"🎮 CPU: S/ {cpu['price']:.0f} ({cpu_pct:.1f}%) - {'✅' if 20 <= cpu_pct <= 35 else '⚠️'}")

print("\n" + "="*70)
print("CASO 2: Oficina básica, 900 soles")
print("="*70)

with SuppressOutput():
    config2 = service.build_pc_configuration("PC básica para oficina, Excel y Word, 900 soles")

if config2['configuration']:
    total = config2['costs']['total']
    budget = config2['costs']['budget']
    print(f"\n💰 Presupuesto: S/ {budget} | Usado: S/ {total:.0f} ({config2['costs']['compliance_percentage']:.1f}%)")
    print(f"   {'✅ Dentro de presupuesto' if config2['costs']['within_budget'] else '⚠️ Excede presupuesto'}")
    
    print(f"\n📦 Componentes:")
    for comp_type, comp in sorted(config2['configuration'].items()):
        pct = (comp['price'] / budget * 100)
        print(f"   {comp_type:12s}: S/ {comp['price']:6.0f} ({pct:5.1f}%)")
    
    mb = config2['configuration'].get('MOTHERBOARD')
    case = config2['configuration'].get('CASE')
    if mb:
        mb_pct = (mb['price'] / budget * 100)
        print(f"\n💼 Motherboard: S/ {mb['price']:.0f} ({mb_pct:.1f}%) - {'✅ Optimizado' if mb_pct <= 15 else '⚠️'}")
    if case:
        case_pct = (case['price'] / budget * 100)
        print(f"💼 Case: S/ {case['price']:.0f} ({case_pct:.1f}%) - {'✅' if case_pct >= 5 else '⚠️'}")

print("\n" + "="*70)

