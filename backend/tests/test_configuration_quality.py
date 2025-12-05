# backend/test_configuration_quality.py
"""Evalúa la calidad de las configuraciones generadas"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from api.pc_builder_service import PCBuilderService

print("\n" + "="*80)
print("🔍 EVALUACIÓN DE CALIDAD DE CONFIGURACIONES")
print("="*80)

service = PCBuilderService()

# Caso 1: Gaming - Valorant con 2000 soles
print("\n" + "="*80)
print("CASO 1: GAMING - Valorant, 2000 soles")
print("="*80)
print("\nAnálisis esperado:")
print("  - Valorant es un juego relativamente ligero")
print("  - Prioridad: GPU (pero no necesita ser muy potente), CPU decente, RAM suficiente")
print("  - Presupuesto: 2000 soles debe ser suficiente para una PC gaming básica/media")
print("\nGenerando configuración...\n")

config1 = service.build_pc_configuration("Quiero una PC para jugar Valorant, tengo 2000 soles")

print("\n" + "="*80)
print("ANÁLISIS DE LA CONFIGURACIÓN GENERADA:")
print("="*80)

if config1['configuration']:
    total = config1['costs']['total']
    budget = config1['costs']['budget']
    
    print(f"\n💰 Presupuesto:")
    print(f"   Asignado: S/ {budget}")
    print(f"   Usado: S/ {total} ({config1['costs']['compliance_percentage']:.1f}%)")
    print(f"   Restante: S/ {config1['costs']['remaining']}")
    
    print(f"\n📦 Componentes seleccionados:")
    for comp_type, comp in config1['configuration'].items():
        price = comp['price']
        percentage = (price / budget * 100) if budget > 0 else 0
        rating = comp.get('predicted_rating', 0)
        print(f"   {comp_type:12s}: {comp['name'][:45]}")
        print(f"      Precio: S/ {price:6.0f} ({percentage:5.1f}%) | Rating: {rating:.2f}")
    
    # Análisis específico para gaming
    print(f"\n🎮 Análisis para Gaming (Valorant):")
    gpu = config1['configuration'].get('GPU')
    cpu = config1['configuration'].get('CPU')
    ram = config1['configuration'].get('RAM')
    
    if gpu:
        gpu_name = gpu['name']
        gpu_price = gpu['price']
        gpu_pct = (gpu_price / budget * 100)
        print(f"   GPU: {gpu_name[:50]}")
        print(f"      Precio: S/ {gpu_price} ({gpu_pct:.1f}% del presupuesto)")
        print(f"      {'✅ Apropiado' if gpu_pct >= 30 and gpu_pct <= 50 else '⚠️ Revisar distribución'}")
    else:
        print(f"   ⚠️  GPU no seleccionada (puede ser problema para gaming)")
    
    if cpu:
        cpu_name = cpu['name']
        cpu_price = cpu['price']
        cpu_pct = (cpu_price / budget * 100)
        print(f"   CPU: {cpu_name[:50]}")
        print(f"      Precio: S/ {cpu_price} ({cpu_pct:.1f}% del presupuesto)")
        print(f"      {'✅ Apropiado' if cpu_pct >= 20 and cpu_pct <= 35 else '⚠️ Revisar distribución'}")
    
    if ram:
        ram_capacity = ram.get('features', {}).get('capacity_gb', 0)
        print(f"   RAM: {ram_capacity}GB - {'✅ Suficiente' if ram_capacity >= 16 else '⚠️ Puede ser insuficiente para gaming moderno'}")

# Caso 2: Oficina básica con 900 soles
print("\n\n" + "="*80)
print("CASO 2: OFICINA BÁSICA - Excel y Word, 900 soles")
print("="*80)
print("\nAnálisis esperado:")
print("  - Uso básico: Excel, Word, navegación web")
print("  - Prioridad: CPU básico pero funcional, RAM suficiente (8GB mínimo), sin GPU necesaria")
print("  - Presupuesto: 900 soles es ajustado, debe optimizarse al máximo")
print("\nGenerando configuración...\n")

config2 = service.build_pc_configuration("PC básica para oficina, Excel y Word, 900 soles")

print("\n" + "="*80)
print("ANÁLISIS DE LA CONFIGURACIÓN GENERADA:")
print("="*80)

if config2['configuration']:
    total = config2['costs']['total']
    budget = config2['costs']['budget']
    
    print(f"\n💰 Presupuesto:")
    print(f"   Asignado: S/ {budget}")
    print(f"   Usado: S/ {total} ({config2['costs']['compliance_percentage']:.1f}%)")
    print(f"   Restante: S/ {config2['costs']['remaining']}")
    
    print(f"\n📦 Componentes seleccionados:")
    for comp_type, comp in config2['configuration'].items():
        price = comp['price']
        percentage = (price / budget * 100) if budget > 0 else 0
        rating = comp.get('predicted_rating', 0)
        print(f"   {comp_type:12s}: {comp['name'][:45]}")
        print(f"      Precio: S/ {price:6.0f} ({percentage:5.1f}%) | Rating: {rating:.2f}")
    
    # Análisis específico para oficina
    print(f"\n💼 Análisis para Oficina Básica:")
    cpu = config2['configuration'].get('CPU')
    ram = config2['configuration'].get('RAM')
    gpu = config2['configuration'].get('GPU')
    
    if cpu:
        cpu_name = cpu['name']
        cpu_price = cpu['price']
        cpu_pct = (cpu_price / budget * 100)
        cpu_cores = cpu.get('features', {}).get('cores', 0)
        print(f"   CPU: {cpu_name[:50]}")
        print(f"      Precio: S/ {cpu_price} ({cpu_pct:.1f}% del presupuesto)")
        print(f"      Cores: {cpu_cores}")
        print(f"      {'✅ Apropiado para oficina' if cpu_cores >= 4 and cpu_pct <= 50 else '⚠️ Revisar'}")
    
    if ram:
        ram_capacity = ram.get('features', {}).get('capacity_gb', 0)
        ram_price = ram['price']
        ram_pct = (ram_price / budget * 100)
        print(f"   RAM: {ram_capacity}GB - S/ {ram_price} ({ram_pct:.1f}%)")
        print(f"      {'✅ Suficiente para oficina' if ram_capacity >= 8 else '⚠️ Puede ser insuficiente'}")
    
    if gpu:
        print(f"   ⚠️  GPU seleccionada (S/ {gpu['price']}) - No necesaria para oficina básica")
        print(f"      Se podría usar CPU con gráficos integrados y ahorrar dinero")
    else:
        print(f"   ✅ Sin GPU (correcto para oficina básica)")

print("\n" + "="*80)
print("✅ EVALUACIÓN COMPLETADA")
print("="*80 + "\n")

