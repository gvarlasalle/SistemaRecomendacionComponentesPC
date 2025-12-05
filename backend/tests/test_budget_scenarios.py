# backend/test_budget_scenarios.py
"""Prueba completa de diferentes escenarios de presupuesto"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from api.pc_builder_service import PCBuilderService

print("\n" + "="*80)
print("🧪 PRUEBA COMPLETA: Escenarios de Presupuesto")
print("="*80)

service = PCBuilderService()

# ==================== CASO 1: PRESUPUESTO ALTO - Diseño + Edición + Gaming + Streaming ====================
print("\n" + "="*80)
print("📊 CASO 1: PRESUPUESTO ALTO - Diseño + Edición + Gaming + Streaming")
print("="*80)
print("💬 Solicitud: 'quiero una pc para diseño gráfico, edición de videos, jugar y hacer streams mi presupuesto es de 6000 soles'")
print("🎯 Objetivo: Máximo rendimiento con componentes de gama alta")
print()

config1 = service.build_pc_configuration("quiero una pc para diseño gráfico, edición de videos, jugar y hacer streams mi presupuesto es de 6000 soles")

if config1['configuration']:
    budget = config1['costs']['budget']
    total = config1['costs']['total']
    
    print(f"\n📊 ANÁLISIS:")
    print(f"   Presupuesto: S/ {budget:,.0f}")
    print(f"   Usado: S/ {total:,.0f} ({config1['costs']['compliance_percentage']:.1f}%)")
    print(f"   Restante: S/ {budget - total:,.0f}")
    
    cpu = config1['configuration'].get('CPU')
    gpu = config1['configuration'].get('GPU')
    ram = config1['configuration'].get('RAM')
    
    if cpu:
        cpu_name = cpu['name'].upper()
        is_high_end = any(x in cpu_name for x in ['RYZEN 7', 'RYZEN 9', 'CORE I7', 'CORE I9'])
        is_mid = any(x in cpu_name for x in ['RYZEN 5', 'CORE I5'])
        print(f"\n   CPU: {cpu['name'][:50]}")
        print(f"      Precio: S/ {cpu['price']:.0f} ({(cpu['price']/budget*100):.1f}%) | Rating: {cpu['predicted_rating']:.2f}")
        if is_high_end:
            print(f"      ✅ Gama alta - Apropiado para presupuesto alto")
        elif is_mid:
            print(f"      ⚠️  Gama media - Para 6000 soles debería ser gama alta")
        else:
            print(f"      ❌ Gama baja - INADECUADO")
    
    if gpu:
        gpu_pct = (gpu['price'] / budget * 100)
        print(f"\n   GPU: {gpu['name'][:50]}")
        print(f"      Precio: S/ {gpu['price']:.0f} ({gpu_pct:.1f}%) | Rating: {gpu['predicted_rating']:.2f}")
        if gpu_pct >= 35:
            print(f"      ✅ Presupuesto adecuado ({gpu_pct:.1f}%)")
        else:
            print(f"      ⚠️  Presupuesto bajo ({gpu_pct:.1f}%)")
    
    if ram:
        ram_capacity = ram.get('features', {}).get('capacity_gb', 0)
        print(f"\n   RAM: {ram_capacity}GB - S/ {ram['price']:.0f} ({(ram['price']/budget*100):.1f}%)")
        if ram_capacity >= 32:
            print(f"      ✅ Generosa (32GB+) - Ideal para edición")
        elif ram_capacity >= 16:
            print(f"      ⚠️  Suficiente pero podría ser más (32GB ideal)")

# ==================== CASO 2: PRESUPUESTO ALTO - Gaming de Alto Rendimiento ====================
print("\n\n" + "="*80)
print("📊 CASO 2: PRESUPUESTO ALTO - Gaming de Alto Rendimiento")
print("="*80)
print("💬 Solicitud: 'PC para gaming de alto rendimiento, quiero jugar juegos AAA en 4K, tengo 5000 soles'")
print("🎯 Objetivo: Máxima potencia para gaming")
print()

config2 = service.build_pc_configuration("PC para gaming de alto rendimiento, quiero jugar juegos AAA en 4K, tengo 5000 soles")

if config2['configuration']:
    budget = config2['costs']['budget']
    total = config2['costs']['total']
    
    print(f"\n📊 ANÁLISIS:")
    print(f"   Presupuesto: S/ {budget:,.0f}")
    print(f"   Usado: S/ {total:,.0f} ({config2['costs']['compliance_percentage']:.1f}%)")
    
    cpu = config2['configuration'].get('CPU')
    gpu = config2['configuration'].get('GPU')
    
    if cpu:
        cpu_name = cpu['name'].upper()
        is_high_end = any(x in cpu_name for x in ['RYZEN 7', 'RYZEN 9', 'CORE I7', 'CORE I9'])
        print(f"\n   CPU: {cpu['name'][:50]}")
        print(f"      {'✅ Gama alta' if is_high_end else '⚠️  Revisar gama'}")
    
    if gpu:
        gpu_pct = (gpu['price'] / budget * 100)
        print(f"\n   GPU: {gpu['name'][:50]}")
        print(f"      Presupuesto: {gpu_pct:.1f}% | Rating: {gpu['predicted_rating']:.2f}")

# ==================== CASO 3: PRESUPUESTO ALTO - Desarrollo Profesional ====================
print("\n\n" + "="*80)
print("📊 CASO 3: PRESUPUESTO ALTO - Desarrollo Profesional")
print("="*80)
print("💬 Solicitud: 'PC para desarrollo profesional, programación, compilación pesada y virtualización, 4500 soles'")
print("🎯 Objetivo: CPU potente y RAM generosa")
print()

config3 = service.build_pc_configuration("PC para desarrollo profesional, programación, compilación pesada y virtualización, 4500 soles")

if config3['configuration']:
    budget = config3['costs']['budget']
    total = config3['costs']['total']
    
    print(f"\n📊 ANÁLISIS:")
    print(f"   Presupuesto: S/ {budget:,.0f}")
    print(f"   Usado: S/ {total:,.0f} ({config3['costs']['compliance_percentage']:.1f}%)")
    
    cpu = config3['configuration'].get('CPU')
    ram = config3['configuration'].get('RAM')
    
    if cpu:
        cpu_name = cpu['name'].upper()
        is_high_end = any(x in cpu_name for x in ['RYZEN 7', 'RYZEN 9', 'CORE I7', 'CORE I9'])
        print(f"\n   CPU: {cpu['name'][:50]}")
        print(f"      {'✅ Gama alta' if is_high_end else '⚠️  Revisar gama'}")
    
    if ram:
        ram_capacity = ram.get('features', {}).get('capacity_gb', 0)
        print(f"\n   RAM: {ram_capacity}GB")
        print(f"      {'✅ Generosa para desarrollo' if ram_capacity >= 32 else '⚠️  Podría ser más' if ram_capacity >= 16 else '❌ Insuficiente'}")

# ==================== CASO 4: PRESUPUESTO EXTREMADAMENTE BAJO - Gaming ====================
print("\n\n" + "="*80)
print("📊 CASO 4: PRESUPUESTO EXTREMADAMENTE BAJO - Gaming")
print("="*80)
print("💬 Solicitud: 'Quiero una PC para jugar, tengo solo 800 soles'")
print("🎯 Objetivo: Optimizar al máximo, componentes básicos pero funcionales")
print()

config4 = service.build_pc_configuration("Quiero una PC para jugar, tengo solo 800 soles")

if config4['configuration']:
    budget = config4['costs']['budget']
    total = config4['costs']['total']
    
    print(f"\n📊 ANÁLISIS:")
    print(f"   Presupuesto: S/ {budget:,.0f}")
    print(f"   Usado: S/ {total:,.0f} ({config4['costs']['compliance_percentage']:.1f}%)")
    
    if config4['costs']['compliance_percentage'] > 110:
        print(f"   ⚠️  Excede significativamente el presupuesto")
    
    cpu = config4['configuration'].get('CPU')
    gpu = config4['configuration'].get('GPU')
    
    if cpu:
        print(f"\n   CPU: {cpu['name'][:50]}")
        print(f"      Precio: S/ {cpu['price']:.0f} ({(cpu['price']/budget*100):.1f}%)")
    
    if gpu:
        print(f"\n   GPU: {gpu['name'][:50]}")
        print(f"      Precio: S/ {gpu['price']:.0f} ({(gpu['price']/budget*100):.1f}%)")

# ==================== CASO 5: PRESUPUESTO EXTREMADAMENTE BAJO - Oficina ====================
print("\n\n" + "="*80)
print("📊 CASO 5: PRESUPUESTO EXTREMADAMENTE BAJO - Oficina")
print("="*80)
print("💬 Solicitud: 'PC básica para oficina, solo Word y Excel, tengo 600 soles'")
print("🎯 Objetivo: Mínimo necesario para tareas básicas")
print()

config5 = service.build_pc_configuration("PC básica para oficina, solo Word y Excel, tengo 600 soles")

if config5['configuration']:
    budget = config5['costs']['budget']
    total = config5['costs']['total']
    
    print(f"\n📊 ANÁLISIS:")
    print(f"   Presupuesto: S/ {budget:,.0f}")
    print(f"   Usado: S/ {total:,.0f} ({config5['costs']['compliance_percentage']:.1f}%)")
    
    cpu = config5['configuration'].get('CPU')
    
    if cpu:
        print(f"\n   CPU: {cpu['name'][:50]}")
        print(f"      Precio: S/ {cpu['price']:.0f} ({(cpu['price']/budget*100):.1f}%)")
        print(f"      {'✅ Adecuado para oficina básica' if cpu['price'] <= budget * 0.5 else '⚠️  Puede optimizarse'}")

# ==================== CASO 6: PRESUPUESTO EXTREMADAMENTE BAJO - Desarrollo ====================
print("\n\n" + "="*80)
print("📊 CASO 6: PRESUPUESTO EXTREMADAMENTE BAJO - Desarrollo")
print("="*80)
print("💬 Solicitud: 'PC para programar Python básico, tengo 700 soles'")
print("🎯 Objetivo: CPU decente y RAM suficiente para desarrollo básico")
print()

config6 = service.build_pc_configuration("PC para programar Python básico, tengo 700 soles")

if config6['configuration']:
    budget = config6['costs']['budget']
    total = config6['costs']['total']
    
    print(f"\n📊 ANÁLISIS:")
    print(f"   Presupuesto: S/ {budget:,.0f}")
    print(f"   Usado: S/ {total:,.0f} ({config6['costs']['compliance_percentage']:.1f}%)")
    
    cpu = config6['configuration'].get('CPU')
    ram = config6['configuration'].get('RAM')
    
    if cpu:
        print(f"\n   CPU: {cpu['name'][:50]}")
        print(f"      Precio: S/ {cpu['price']:.0f} ({(cpu['price']/budget*100):.1f}%)")
    
    if ram:
        ram_capacity = ram.get('features', {}).get('capacity_gb', 0)
        print(f"\n   RAM: {ram_capacity}GB")
        print(f"      {'✅ Suficiente para desarrollo básico' if ram_capacity >= 8 else '⚠️  Muy limitado'}")

# ==================== CASO 7: PRESUPUESTO ALTO - Workstation Profesional ====================
print("\n\n" + "="*80)
print("📊 CASO 7: PRESUPUESTO ALTO - Workstation Profesional")
print("="*80)
print("💬 Solicitud: 'PC workstation para diseño 3D, renderizado y animación, presupuesto 5500 soles'")
print("🎯 Objetivo: Máximo rendimiento en CPU, GPU y RAM")
print()

config7 = service.build_pc_configuration("PC workstation para diseño 3D, renderizado y animación, presupuesto 5500 soles")

if config7['configuration']:
    budget = config7['costs']['budget']
    total = config7['costs']['total']
    
    print(f"\n📊 ANÁLISIS:")
    print(f"   Presupuesto: S/ {budget:,.0f}")
    print(f"   Usado: S/ {total:,.0f} ({config7['costs']['compliance_percentage']:.1f}%)")
    
    cpu = config7['configuration'].get('CPU')
    gpu = config7['configuration'].get('GPU')
    ram = config7['configuration'].get('RAM')
    
    if cpu:
        cpu_name = cpu['name'].upper()
        is_high_end = any(x in cpu_name for x in ['RYZEN 7', 'RYZEN 9', 'CORE I7', 'CORE I9'])
        print(f"\n   CPU: {cpu['name'][:50]}")
        print(f"      {'✅ Gama alta' if is_high_end else '⚠️  Revisar gama'}")
    
    if gpu:
        gpu_pct = (gpu['price'] / budget * 100)
        print(f"\n   GPU: {gpu['name'][:50]}")
        print(f"      Presupuesto: {gpu_pct:.1f}%")
    
    if ram:
        ram_capacity = ram.get('features', {}).get('capacity_gb', 0)
        print(f"\n   RAM: {ram_capacity}GB")
        print(f"      {'✅ Generosa para renderizado' if ram_capacity >= 32 else '⚠️  Podría ser más'}")

# ==================== RESUMEN FINAL ====================
print("\n\n" + "="*80)
print("📋 RESUMEN DE TODOS LOS CASOS")
print("="*80)

cases = [
    ("Caso 1: Alto - Diseño+Gaming+Streaming (6000)", config1),
    ("Caso 2: Alto - Gaming 4K (5000)", config2),
    ("Caso 3: Alto - Desarrollo (4500)", config3),
    ("Caso 4: Bajo - Gaming (800)", config4),
    ("Caso 5: Bajo - Oficina (600)", config5),
    ("Caso 6: Bajo - Desarrollo (700)", config6),
    ("Caso 7: Alto - Workstation (5500)", config7),
]

print(f"\n{'Caso':<45} {'Presupuesto':<12} {'Usado':<12} {'%':<8} {'Estado'}")
print("-" * 80)

for case_name, config in cases:
    if config and config['configuration']:
        budget = config['costs']['budget']
        total = config['costs']['total']
        pct = config['costs']['compliance_percentage']
        
        if pct <= 105:
            status = "✅ OK"
        elif pct <= 110:
            status = "⚠️  Exceso"
        else:
            status = "❌ Alto exceso"
        
        print(f"{case_name:<45} S/ {budget:>7,.0f}  S/ {total:>7,.0f}  {pct:>5.1f}%  {status}")

print("\n" + "="*80)
print("✅ PRUEBA COMPLETA FINALIZADA")
print("="*80)
print("\n💡 OBSERVACIONES:")
print("   • Presupuestos altos (>3000): Deben usar componentes de gama alta")
print("   • Presupuestos altos: Deben aprovechar mejor el presupuesto (80%+)")
print("   • Presupuestos bajos (<1200): Deben optimizar al máximo y respetar presupuesto")
print("   • Presupuestos extremadamente bajos (<800): Pueden tener limitaciones")
print("="*80 + "\n")

