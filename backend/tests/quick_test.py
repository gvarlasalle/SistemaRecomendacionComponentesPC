# backend/quick_test.py
"""Prueba rápida de los casos específicos"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from api.pc_builder_service import PCBuilderService
import io
from contextlib import redirect_stdout

# Redirigir salida para evitar spam
f = io.StringIO()

service = PCBuilderService()

print("\n" + "="*70)
print("CASO 1: Gaming - Valorant, 2000 soles")
print("="*70)

with redirect_stdout(f):
    config1 = service.build_pc_configuration("Quiero una PC para jugar Valorant, tengo 2000 soles")

if config1['configuration']:
    total = config1['costs']['total']
    budget = config1['costs']['budget']
    print(f"\n💰 Presupuesto: S/ {budget} | Usado: S/ {total:.0f} ({config1['costs']['compliance_percentage']:.1f}%)")
    print(f"   {'✅ Dentro de presupuesto' if config1['costs']['within_budget'] else '⚠️ Excede presupuesto'}")
    
    print(f"\n📦 Componentes:")
    for comp_type, comp in config1['configuration'].items():
        pct = (comp['price'] / budget * 100)
        print(f"   {comp_type:12s}: S/ {comp['price']:6.0f} ({pct:5.1f}%) | {comp['name'][:40]}")
    
    gpu = config1['configuration'].get('GPU')
    cpu = config1['configuration'].get('CPU')
    print(f"\n🎮 Análisis Gaming:")
    if gpu:
        gpu_pct = (gpu['price'] / budget * 100)
        print(f"   GPU: S/ {gpu['price']:.0f} ({gpu_pct:.1f}%) - {'✅ Apropiado' if 30 <= gpu_pct <= 50 else '⚠️ Revisar'}")
    if cpu:
        cpu_pct = (cpu['price'] / budget * 100)
        print(f"   CPU: S/ {cpu['price']:.0f} ({cpu_pct:.1f}%) - {'✅ Apropiado' if 20 <= cpu_pct <= 35 else '⚠️ Revisar'}")

print("\n" + "="*70)
print("CASO 2: Oficina básica, 900 soles")
print("="*70)

with redirect_stdout(f):
    config2 = service.build_pc_configuration("PC básica para oficina, Excel y Word, 900 soles")

if config2['configuration']:
    total = config2['costs']['total']
    budget = config2['costs']['budget']
    print(f"\n💰 Presupuesto: S/ {budget} | Usado: S/ {total:.0f} ({config2['costs']['compliance_percentage']:.1f}%)")
    print(f"   {'✅ Dentro de presupuesto' if config2['costs']['within_budget'] else '⚠️ Excede presupuesto'}")
    
    print(f"\n📦 Componentes:")
    for comp_type, comp in config2['configuration'].items():
        pct = (comp['price'] / budget * 100)
        print(f"   {comp_type:12s}: S/ {comp['price']:6.0f} ({pct:5.1f}%) | {comp['name'][:40]}")
    
    mb = config2['configuration'].get('MOTHERBOARD')
    case = config2['configuration'].get('CASE')
    print(f"\n💼 Análisis Oficina:")
    if mb:
        mb_pct = (mb['price'] / budget * 100)
        print(f"   Motherboard: S/ {mb['price']:.0f} ({mb_pct:.1f}%) - {'✅ Optimizado' if mb_pct <= 15 else '⚠️ Muy caro'}")
    if case:
        case_pct = (case['price'] / budget * 100)
        print(f"   Case: S/ {case['price']:.0f} ({case_pct:.1f}%) - {'✅ Apropiado' if case_pct >= 5 else '⚠️ Muy barato'}")

print("\n" + "="*70)
print("✅ PRUEBAS COMPLETADAS")
print("="*70 + "\n")

