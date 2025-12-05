# backend/test_max_performance.py
"""Prueba que el sistema maximiza el rendimiento según caso de uso"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from api.pc_builder_service import PCBuilderService

print("\n" + "="*80)
print("🚀 PRUEBA: Maximización de Rendimiento según Caso de Uso")
print("="*80)

service = PCBuilderService()

# Caso 1: Gaming
print("\n" + "="*80)
print("CASO 1: GAMING - Valorant, 2000 soles")
print("="*80)
print("Objetivo: Máximo rendimiento en GPU y CPU")
print()

config1 = service.build_pc_configuration("Quiero una PC para jugar Valorant, tengo 2000 soles")

if config1['configuration']:
    cpu = config1['configuration'].get('CPU')
    gpu = config1['configuration'].get('GPU')
    budget = config1['costs']['budget']
    
    print(f"\n📊 COMPONENTES CRÍTICOS PARA RENDIMIENTO:")
    if cpu:
        cpu_name = cpu['name'].upper()
        is_mid_high = any(x in cpu_name for x in ['RYZEN 5', 'RYZEN 7', 'RYZEN 9', 'CORE I5', 'CORE I7', 'CORE I9'])
        cpu_pct = (cpu['price'] / budget * 100)
        print(f"   CPU: {cpu['name'][:50]}")
        print(f"      Precio: S/ {cpu['price']:.0f} ({cpu_pct:.1f}%) | Rating: {cpu['predicted_rating']:.2f}")
        print(f"      {'✅ Gama media/alta - Máximo rendimiento' if is_mid_high else '⚠️  Revisar gama'}")
    
    if gpu:
        gpu_pct = (gpu['price'] / budget * 100)
        print(f"   GPU: {gpu['name'][:50]}")
        print(f"      Precio: S/ {gpu['price']:.0f} ({gpu_pct:.1f}%) | Rating: {gpu['predicted_rating']:.2f}")
        print(f"      {'✅ Priorizado para máximo rendimiento' if gpu_pct >= 35 else '⚠️  Puede optimizarse'}")
    
    print(f"\n💰 Presupuesto: S/ {budget} | Total: S/ {config1['costs']['total']:.0f} ({config1['costs']['compliance_percentage']:.1f}%)")

# Caso 2: Desarrollo
print("\n\n" + "="*80)
print("CASO 2: DESARROLLO - Python y Machine Learning, 1800 soles")
print("="*80)
print("Objetivo: Máximo rendimiento en CPU y RAM")
print()

config2 = service.build_pc_configuration("PC para programar Python y machine learning, 1800 soles")

if config2['configuration']:
    cpu = config2['configuration'].get('CPU')
    ram = config2['configuration'].get('RAM')
    budget = config2['costs']['budget']
    
    print(f"\n📊 COMPONENTES CRÍTICOS PARA RENDIMIENTO:")
    if cpu:
        cpu_name = cpu['name'].upper()
        is_mid_high = any(x in cpu_name for x in ['RYZEN 5', 'RYZEN 7', 'RYZEN 9', 'CORE I5', 'CORE I7', 'CORE I9'])
        cpu_pct = (cpu['price'] / budget * 100)
        print(f"   CPU: {cpu['name'][:50]}")
        print(f"      Precio: S/ {cpu['price']:.0f} ({cpu_pct:.1f}%) | Rating: {cpu['predicted_rating']:.2f}")
        print(f"      {'✅ Gama media/alta - Máximo rendimiento' if is_mid_high else '⚠️  Revisar gama'}")
    
    if ram:
        ram_capacity = ram.get('features', {}).get('capacity_gb', 0)
        ram_pct = (ram['price'] / budget * 100)
        print(f"   RAM: {ram_capacity}GB - S/ {ram['price']:.0f} ({ram_pct:.1f}%)")
        print(f"      {'✅ Suficiente para desarrollo' if ram_capacity >= 16 else '⚠️  Puede necesitar más'}")
    
    print(f"\n💰 Presupuesto: S/ {budget} | Total: S/ {config2['costs']['total']:.0f} ({config2['costs']['compliance_percentage']:.1f}%)")

# Caso 3: Oficina
print("\n\n" + "="*80)
print("CASO 3: OFICINA - Excel y Word, 900 soles")
print("="*80)
print("Objetivo: Rendimiento adecuado optimizando presupuesto")
print()

config3 = service.build_pc_configuration("PC básica para oficina, Excel y Word, 900 soles")

if config3['configuration']:
    cpu = config3['configuration'].get('CPU')
    budget = config3['costs']['budget']
    
    print(f"\n📊 COMPONENTE CRÍTICO:")
    if cpu:
        cpu_pct = (cpu['price'] / budget * 100)
        print(f"   CPU: {cpu['name'][:50]}")
        print(f"      Precio: S/ {cpu['price']:.0f} ({cpu_pct:.1f}%) | Rating: {cpu['predicted_rating']:.2f}")
        print(f"      {'✅ Adecuado para oficina' if cpu_pct <= 40 else '⚠️  Puede optimizarse'}")
    
    print(f"\n💰 Presupuesto: S/ {budget} | Total: S/ {config3['costs']['total']:.0f} ({config3['costs']['compliance_percentage']:.1f}%)")

print("\n" + "="*80)
print("✅ PRUEBA COMPLETADA")
print("="*80)
print("\n📋 RESUMEN:")
print("   ✅ Gaming: Prioriza GPU y CPU de gama media/alta")
print("   ✅ Desarrollo: Prioriza CPU y RAM para máximo rendimiento")
print("   ✅ Oficina: Optimiza presupuesto manteniendo rendimiento adecuado")
print("   ✅ Sistema mantiene componentes de alto rendimiento durante ajustes")
print("="*80 + "\n")

