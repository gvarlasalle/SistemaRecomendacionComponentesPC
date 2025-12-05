# backend/test_mejoras.py
"""Prueba las mejoras de priorización y distribución de presupuesto"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from api.pc_builder_service import PCBuilderService

print("\n" + "="*80)
print("🧪 PRUEBA DE MEJORAS: Priorización y Distribución de Presupuesto")
print("="*80)

service = PCBuilderService()

# Caso 1: Gaming - Valorant
print("\n" + "="*80)
print("CASO 1: Gaming - Valorant, 2000 soles")
print("="*80)
print("\nAnálisis esperado:")
print("  - GPU debe ser prioridad (40% = S/ 800)")
print("  - CPU importante pero secundario (25% = S/ 500)")
print("  - Presupuesto: 2000 soles (normal, no bajo)")
print()

config1 = service.build_pc_configuration("Quiero una PC para jugar Valorant, tengo 2000 soles")

if config1['configuration']:
    total = config1['costs']['total']
    budget = config1['costs']['budget']
    
    print("\n" + "="*80)
    print("📊 ANÁLISIS DE RESULTADO:")
    print("="*80)
    print(f"\n💰 Presupuesto:")
    print(f"   Asignado: S/ {budget}")
    print(f"   Usado: S/ {total:.0f} ({config1['costs']['compliance_percentage']:.1f}%)")
    print(f"   {'✅ Dentro de presupuesto' if config1['costs']['within_budget'] else '⚠️ Excede presupuesto'}")
    
    print(f"\n📦 Componentes seleccionados:")
    for comp_type, comp in config1['configuration'].items():
        price = comp['price']
        percentage = (price / budget * 100) if budget > 0 else 0
        print(f"   {comp_type:12s}: S/ {price:6.0f} ({percentage:5.1f}%) | {comp['name'][:40]}")
    
    gpu = config1['configuration'].get('GPU')
    cpu = config1['configuration'].get('CPU')
    
    print(f"\n🎮 Análisis para Gaming:")
    if gpu:
        gpu_pct = (gpu['price'] / budget * 100)
        print(f"   GPU: S/ {gpu['price']:.0f} ({gpu_pct:.1f}%)")
        if 30 <= gpu_pct <= 50:
            print(f"      ✅ Apropiado para gaming (30-50% esperado)")
        else:
            print(f"      ⚠️  Revisar distribución (esperado 30-50%)")
    else:
        print(f"   ⚠️  GPU no seleccionada (problema para gaming)")
    
    if cpu:
        cpu_pct = (cpu['price'] / budget * 100)
        print(f"   CPU: S/ {cpu['price']:.0f} ({cpu_pct:.1f}%)")
        if 20 <= cpu_pct <= 35:
            print(f"      ✅ Apropiado para gaming (20-35% esperado)")
        else:
            print(f"      ⚠️  Revisar distribución (esperado 20-35%)")

# Caso 2: Oficina básica
print("\n\n" + "="*80)
print("CASO 2: Oficina básica, 900 soles")
print("="*80)
print("\nAnálisis esperado:")
print("  - Presupuesto bajo (< 1200) - optimización agresiva")
print("  - Motherboard reducido (12% = S/ 108 vs 18% anterior)")
print("  - CASE con más presupuesto (8% = S/ 72 vs 2% anterior)")
print("  - CPU importante pero optimizado (35% = S/ 315)")
print("  - Máximo 5% de exceso permitido")
print()

config2 = service.build_pc_configuration("PC básica para oficina, Excel y Word, 900 soles")

if config2['configuration']:
    total = config2['costs']['total']
    budget = config2['costs']['budget']
    
    print("\n" + "="*80)
    print("📊 ANÁLISIS DE RESULTADO:")
    print("="*80)
    print(f"\n💰 Presupuesto:")
    print(f"   Asignado: S/ {budget}")
    print(f"   Usado: S/ {total:.0f} ({config2['costs']['compliance_percentage']:.1f}%)")
    print(f"   {'✅ Dentro de presupuesto' if config2['costs']['within_budget'] else '⚠️ Excede presupuesto'}")
    
    print(f"\n📦 Componentes seleccionados:")
    for comp_type, comp in config2['configuration'].items():
        price = comp['price']
        percentage = (price / budget * 100) if budget > 0 else 0
        allocated_pct = 0.35 if comp_type == 'CPU' else 0.20 if comp_type == 'RAM' else 0.12 if comp_type == 'MOTHERBOARD' else 0.15 if comp_type == 'STORAGE' else 0.10 if comp_type == 'PSU' else 0.08
        allocated = budget * allocated_pct
        status = "✅" if price <= allocated * 1.1 else "⚠️"
        print(f"   {status} {comp_type:12s}: S/ {price:6.0f} ({percentage:5.1f}%) | Esperado: ~{allocated_pct*100:.0f}% | {comp['name'][:35]}")
    
    mb = config2['configuration'].get('MOTHERBOARD')
    case = config2['configuration'].get('CASE')
    cpu = config2['configuration'].get('CPU')
    
    print(f"\n💼 Análisis para Oficina (Presupuesto Bajo):")
    if mb:
        mb_pct = (mb['price'] / budget * 100)
        print(f"   Motherboard: S/ {mb['price']:.0f} ({mb_pct:.1f}%)")
        if mb_pct <= 15:
            print(f"      ✅ Optimizado (esperado ≤15% para presupuesto bajo)")
        else:
            print(f"      ⚠️  Puede optimizarse más (esperado ≤15%)")
    
    if case:
        case_pct = (case['price'] / budget * 100)
        print(f"   CASE: S/ {case['price']:.0f} ({case_pct:.1f}%)")
        if case_pct >= 5:
            print(f"      ✅ Con presupuesto adecuado (esperado ≥5% para presupuesto bajo)")
        else:
            print(f"      ⚠️  Puede necesitar más presupuesto")
    
    if cpu:
        cpu_pct = (cpu['price'] / budget * 100)
        print(f"   CPU: S/ {cpu['price']:.0f} ({cpu_pct:.1f}%)")
        if 30 <= cpu_pct <= 40:
            print(f"      ✅ Apropiado para oficina (30-40% esperado)")
        else:
            print(f"      ⚠️  Revisar distribución")

print("\n" + "="*80)
print("✅ PRUEBA COMPLETADA")
print("="*80 + "\n")

