# backend/test_high_budget.py
"""Prueba con presupuesto alto: diseño, edición, gaming y streaming"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from api.pc_builder_service import PCBuilderService
from api.recommendation_service import RecommendationService

print("\n" + "="*80)
print("🎨 PRUEBA: Presupuesto Alto - Diseño, Edición, Gaming y Streaming")
print("="*80)

service = PCBuilderService()
recommender = RecommendationService()

# Caso: Diseño gráfico, edición de videos, gaming y streaming - 6000 soles
print("\n💬 Solicitud: 'quiero una pc para diseño gráfico, edición de videos, jugar y hacer streams mi presupuesto es de 6000 soles'")
print("="*80)
print("\n📊 Análisis esperado:")
print("   - Presupuesto ALTO (6000 soles)")
print("   - Múltiples casos de uso: diseño, edición, gaming, streaming")
print("   - Debería seleccionar componentes de ALTA GAMA")
print("   - GPU potente (edición de video, gaming, streaming)")
print("   - CPU potente (edición de video, streaming)")
print("   - RAM generosa (32GB+ ideal)")
print("   - Storage rápido (NVMe M.2)")
print()

config = service.build_pc_configuration("quiero una pc para diseño gráfico, edición de videos, jugar y hacer streams mi presupuesto es de 6000 soles")

if config['configuration']:
    budget = config['costs']['budget']
    total = config['costs']['total']
    
    print("\n" + "="*80)
    print("📊 ANÁLISIS DE LA CONFIGURACIÓN GENERADA:")
    print("="*80)
    
    print(f"\n💰 Presupuesto:")
    print(f"   Asignado: S/ {budget:,.0f}")
    print(f"   Usado: S/ {total:,.0f} ({config['costs']['compliance_percentage']:.1f}%)")
    print(f"   Restante: S/ {budget - total:,.0f}")
    
    if config['costs']['compliance_percentage'] < 80:
        print(f"   ⚠️  PROBLEMA: Solo se está usando {config['costs']['compliance_percentage']:.1f}% del presupuesto")
        print(f"   ⚠️  Se podría seleccionar componentes de mayor gama")
    
    print(f"\n📦 Componentes seleccionados:")
    for comp_type, comp in config['configuration'].items():
        price = comp['price']
        percentage = (price / budget * 100) if budget > 0 else 0
        rating = comp.get('predicted_rating', 0)
        print(f"   {comp_type:12s}: S/ {price:6.0f} ({percentage:5.1f}%) | Rating: {rating:.2f}")
        print(f"                {comp['name'][:60]}")
    
    # Análisis específico
    print(f"\n🎯 ANÁLISIS POR COMPONENTE CRÍTICO:")
    
    cpu = config['configuration'].get('CPU')
    if cpu:
        cpu_name = cpu['name'].upper()
        cpu_price = cpu['price']
        cpu_pct = (cpu_price / budget * 100)
        is_high_end = any(x in cpu_name for x in ['RYZEN 7', 'RYZEN 9', 'CORE I7', 'CORE I9'])
        is_mid = any(x in cpu_name for x in ['RYZEN 5', 'CORE I5'])
        
        print(f"\n   CPU: {cpu['name'][:50]}")
        print(f"      Precio: S/ {cpu_price:.0f} ({cpu_pct:.1f}%)")
        if is_high_end:
            print(f"      ✅ Gama alta - Apropiado para presupuesto alto")
        elif is_mid:
            print(f"      ⚠️  Gama media - Para 6000 soles debería ser gama alta (Ryzen 7/9 o Core i7/i9)")
        else:
            print(f"      ❌ Gama baja - INADECUADO para presupuesto de 6000 soles")
    
    gpu = config['configuration'].get('GPU')
    if gpu:
        gpu_price = gpu['price']
        gpu_pct = (gpu_price / budget * 100)
        gpu_name = gpu['name'].upper()
        is_high_end = any(x in gpu_name for x in ['RTX 3060', 'RTX 3070', 'RTX 3080', 'RTX 4060', 'RTX 4070', 'RTX 4080', 'RTX 4090',
                                                   'RX 6600', 'RX 6700', 'RX 6800', 'RX 6900', 'RX 7600', 'RX 7700', 'RX 7800', 'RX 7900'])
        
        print(f"\n   GPU: {gpu['name'][:50]}")
        print(f"      Precio: S/ {gpu_price:.0f} ({gpu_pct:.1f}%)")
        if gpu_pct >= 30:
            print(f"      ✅ Presupuesto adecuado ({gpu_pct:.1f}%)")
        else:
            print(f"      ⚠️  Presupuesto bajo ({gpu_pct:.1f}%) - Para 6000 soles debería ser 30-40%")
        if is_high_end:
            print(f"      ✅ GPU de gama alta")
        else:
            print(f"      ⚠️  GPU de gama media/baja - Para edición y gaming debería ser mejor")
    
    ram = config['configuration'].get('RAM')
    if ram:
        ram_capacity = ram.get('features', {}).get('capacity_gb', 0)
        ram_price = ram['price']
        ram_pct = (ram_price / budget * 100)
        
        print(f"\n   RAM: {ram_capacity}GB - S/ {ram_price:.0f} ({ram_pct:.1f}%)")
        if ram_capacity >= 32:
            print(f"      ✅ Generosa (32GB+) - Ideal para edición y streaming")
        elif ram_capacity >= 16:
            print(f"      ⚠️  Suficiente pero podría ser más (32GB ideal para edición)")
        else:
            print(f"      ❌ Insuficiente para edición de video y streaming")
    
    storage = config['configuration'].get('STORAGE')
    if storage:
        storage_type = storage.get('features', {}).get('storage_type', '').upper()
        storage_price = storage['price']
        storage_pct = (storage_price / budget * 100)
        
        print(f"\n   STORAGE: {storage['name'][:50]}")
        print(f"      Precio: S/ {storage_price:.0f} ({storage_pct:.1f}%)")
        if 'M.2' in storage_type or 'NVME' in storage_type:
            print(f"      ✅ NVMe M.2 - Rápido para edición")
        else:
            print(f"      ⚠️  SATA - Para edición debería ser NVMe M.2")
    
    print(f"\n💡 RECOMENDACIONES:")
    if config['costs']['compliance_percentage'] < 80:
        print(f"   ⚠️  El sistema está usando solo {config['costs']['compliance_percentage']:.1f}% del presupuesto")
        print(f"   💡 Debería seleccionar componentes de mayor gama para aprovechar mejor el presupuesto")
    
    if cpu and not any(x in cpu['name'].upper() for x in ['RYZEN 7', 'RYZEN 9', 'CORE I7', 'CORE I9']):
        print(f"   💡 Para 6000 soles, debería seleccionar CPU de gama alta (Ryzen 7/9 o Core i7/i9)")
    
    if gpu and (gpu['price'] / budget * 100) < 30:
        print(f"   💡 Debería asignar más presupuesto a GPU (30-40% para este caso de uso)")
    
    if ram and ram.get('features', {}).get('capacity_gb', 0) < 32:
        print(f"   💡 Para edición de video y streaming, idealmente 32GB de RAM")

print("\n" + "="*80)

