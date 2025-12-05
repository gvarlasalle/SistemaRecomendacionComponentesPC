# backend/test_budget_scenarios_simple.py
"""Prueba simplificada de escenarios de presupuesto"""

import sys
import io
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

# Configurar salida UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from api.pc_builder_service import PCBuilderService

print("\n" + "="*80)
print("PRUEBA: Escenarios de Presupuesto")
print("="*80)

service = PCBuilderService()

# CASO 1: PRESUPUESTO ALTO - Diseño + Edición + Gaming + Streaming
print("\n" + "="*80)
print("CASO 1: PRESUPUESTO ALTO (6000 soles) - Diseno + Edicion + Gaming + Streaming")
print("="*80)
print("Solicitud: 'quiero una pc para diseno grafico, edicion de videos, jugar y hacer streams mi presupuesto es de 6000 soles'")
print()

config1 = service.build_pc_configuration("quiero una pc para diseño gráfico, edición de videos, jugar y hacer streams mi presupuesto es de 6000 soles")

if config1['configuration']:
    budget = config1['costs']['budget']
    total = config1['costs']['total']
    pct = config1['costs']['compliance_percentage']
    
    print(f"\nRESULTADO:")
    print(f"   Presupuesto: S/ {budget:,.0f}")
    print(f"   Usado: S/ {total:,.0f} ({pct:.1f}%)")
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
            print(f"      [OK] Gama alta - Apropiado para presupuesto alto")
        elif is_mid:
            print(f"      [AVISO] Gama media - Para 6000 soles deberia ser gama alta")
        else:
            print(f"      [ERROR] Gama baja - INADECUADO")
    
    if gpu:
        gpu_pct = (gpu['price'] / budget * 100)
        print(f"\n   GPU: {gpu['name'][:50]}")
        print(f"      Precio: S/ {gpu['price']:.0f} ({gpu_pct:.1f}%) | Rating: {gpu['predicted_rating']:.2f}")
        if gpu_pct >= 35:
            print(f"      [OK] Presupuesto adecuado ({gpu_pct:.1f}%)")
        else:
            print(f"      [AVISO] Presupuesto bajo ({gpu_pct:.1f}%) - Deberia ser 35-42%")
    
    if ram:
        ram_capacity = ram.get('features', {}).get('capacity_gb', 0)
        print(f"\n   RAM: {ram_capacity}GB - S/ {ram['price']:.0f} ({(ram['price']/budget*100):.1f}%)")
        if ram_capacity >= 32:
            print(f"      [OK] Generosa (32GB+) - Ideal para edicion")
        elif ram_capacity >= 16:
            print(f"      [AVISO] Suficiente pero podria ser mas (32GB ideal para edicion)")
        else:
            print(f"      [ERROR] Insuficiente para edicion de video")

# CASO 2: PRESUPUESTO EXTREMADAMENTE BAJO - Gaming
print("\n\n" + "="*80)
print("CASO 2: PRESUPUESTO EXTREMADAMENTE BAJO (800 soles) - Gaming")
print("="*80)
print("Solicitud: 'Quiero una PC para jugar, tengo solo 800 soles'")
print()

config2 = service.build_pc_configuration("Quiero una PC para jugar, tengo solo 800 soles")

if config2['configuration']:
    budget = config2['costs']['budget']
    total = config2['costs']['total']
    pct = config2['costs']['compliance_percentage']
    
    print(f"\nRESULTADO:")
    print(f"   Presupuesto: S/ {budget:,.0f}")
    print(f"   Usado: S/ {total:,.0f} ({pct:.1f}%)")
    
    if pct > 110:
        print(f"   [AVISO] Excede significativamente el presupuesto")
    elif pct <= 105:
        print(f"   [OK] Respeta el presupuesto")
    
    cpu = config2['configuration'].get('CPU')
    gpu = config2['configuration'].get('GPU')
    
    if cpu:
        print(f"\n   CPU: {cpu['name'][:50]}")
        print(f"      Precio: S/ {cpu['price']:.0f} ({(cpu['price']/budget*100):.1f}%)")
    
    if gpu:
        print(f"\n   GPU: {gpu['name'][:50]}")
        print(f"      Precio: S/ {gpu['price']:.0f} ({(gpu['price']/budget*100):.1f}%)")

# CASO 3: PRESUPUESTO ALTO - Gaming 4K
print("\n\n" + "="*80)
print("CASO 3: PRESUPUESTO ALTO (5000 soles) - Gaming 4K")
print("="*80)
print("Solicitud: 'PC para gaming de alto rendimiento, quiero jugar juegos AAA en 4K, tengo 5000 soles'")
print()

config3 = service.build_pc_configuration("PC para gaming de alto rendimiento, quiero jugar juegos AAA en 4K, tengo 5000 soles")

if config3['configuration']:
    budget = config3['costs']['budget']
    total = config3['costs']['total']
    pct = config3['costs']['compliance_percentage']
    
    print(f"\nRESULTADO:")
    print(f"   Presupuesto: S/ {budget:,.0f}")
    print(f"   Usado: S/ {total:,.0f} ({pct:.1f}%)")
    
    cpu = config3['configuration'].get('CPU')
    gpu = config3['configuration'].get('GPU')
    
    if cpu:
        cpu_name = cpu['name'].upper()
        is_high_end = any(x in cpu_name for x in ['RYZEN 7', 'RYZEN 9', 'CORE I7', 'CORE I9'])
        print(f"\n   CPU: {cpu['name'][:50]}")
        print(f"      {'[OK] Gama alta' if is_high_end else '[AVISO] Revisar gama'}")
    
    if gpu:
        gpu_pct = (gpu['price'] / budget * 100)
        print(f"\n   GPU: {gpu['name'][:50]}")
        print(f"      Presupuesto: {gpu_pct:.1f}% | Rating: {gpu['predicted_rating']:.2f}")

# RESUMEN
print("\n\n" + "="*80)
print("RESUMEN")
print("="*80)
print(f"{'Caso':<50} {'Presupuesto':<12} {'Usado':<12} {'%':<8} {'Estado'}")
print("-" * 80)

cases = [
    ("Caso 1: Alto - Diseno+Gaming+Streaming (6000)", config1),
    ("Caso 2: Bajo - Gaming (800)", config2),
    ("Caso 3: Alto - Gaming 4K (5000)", config3),
]

for case_name, config in cases:
    if config and config['configuration']:
        budget = config['costs']['budget']
        total = config['costs']['total']
        pct = config['costs']['compliance_percentage']
        
        if pct <= 105:
            status = "[OK]"
        elif pct <= 110:
            status = "[AVISO] Exceso"
        else:
            status = "[ERROR] Alto exceso"
        
        print(f"{case_name:<50} S/ {budget:>7,.0f}  S/ {total:>7,.0f}  {pct:>5.1f}%  {status}")

print("\n" + "="*80)
print("PRUEBA COMPLETADA")
print("="*80 + "\n")

