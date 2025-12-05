# backend/data_layer/analyze_dataset.py
"""
Analiza el dataset actual para ver qué tenemos
y qué nos falta para armar PCs completas
"""

import json
from collections import defaultdict

def analyze_dataset(json_file):
    """Analiza composición del dataset"""
    
    print("\n" + "="*60)
    print("📊 ANÁLISIS DEL DATASET ACTUAL")
    print("="*60)
    
    with open(json_file, 'r', encoding='utf-8') as f:
        components = json.load(f)
    
    print(f"\n📦 Total componentes: {len(components)}")
    
    # Contar por tipo
    by_type = defaultdict(list)
    for comp in components:
        by_type[comp['type']].append(comp)
    
    print("\n📈 Distribución por tipo:")
    for comp_type in sorted(by_type.keys()):
        count = len(by_type[comp_type])
        print(f"   {comp_type:15s}: {count:3d} componentes")
    
    # Análisis de CPUs
    print("\n" + "="*60)
    print("🔍 ANÁLISIS DETALLADO: CPUs")
    print("="*60)
    
    cpus = by_type['CPU']
    sockets = defaultdict(int)
    brands = defaultdict(int)
    
    for cpu in cpus:
        socket = cpu.get('compatibility', {}).get('socket', 'Unknown')
        sockets[socket] += 1
        
        name = cpu['name'].upper()
        if 'INTEL' in name or 'I3' in name or 'I5' in name or 'I7' in name or 'I9' in name:
            brands['Intel'] += 1
        elif 'AMD' in name or 'RYZEN' in name:
            brands['AMD'] += 1
        else:
            brands['Unknown'] += 1
    
    print(f"\n📊 CPUs por marca:")
    for brand, count in sorted(brands.items(), key=lambda x: -x[1]):
        print(f"   {brand:10s}: {count:2d} CPUs")
    
    print(f"\n🔌 CPUs por socket:")
    for socket, count in sorted(sockets.items(), key=lambda x: -x[1]):
        print(f"   {socket:20s}: {count:2d} CPUs")
    
    # Análisis de MOTHERBOARDs
    print("\n" + "="*60)
    print("🔍 ANÁLISIS DETALLADO: MOTHERBOARDs")
    print("="*60)
    
    motherboards = by_type['MOTHERBOARD']
    mb_sockets = defaultdict(int)
    
    print(f"\n📦 Total motherboards: {len(motherboards)}")
    
    if motherboards:
        for mb in motherboards:
            socket = mb.get('compatibility', {}).get('socket', 'Unknown')
            mb_sockets[socket] += 1
            print(f"\n   ID: {mb['id']}")
            print(f"   Nombre: {mb['name'][:60]}")
            print(f"   Socket: {socket}")
            print(f"   Precio: S/ {mb['regular_price']}")
        
        print(f"\n🔌 Motherboards por socket:")
        for socket, count in sorted(mb_sockets.items(), key=lambda x: -x[1]):
            print(f"   {socket:20s}: {count:2d} motherboards")
    else:
        print("   ⚠️  No hay motherboards en el dataset")
    
    # COMPATIBILIDAD: CPU vs MOTHERBOARD
    print("\n" + "="*60)
    print("⚠️  PROBLEMA DE COMPATIBILIDAD")
    print("="*60)
    
    print(f"\n🔌 Sockets de CPUs disponibles:")
    for socket in sorted(sockets.keys()):
        cpu_count = sockets[socket]
        mb_count = mb_sockets.get(socket, 0)
        status = "✅" if mb_count > 0 else "❌"
        print(f"   {status} {socket:20s}: {cpu_count:2d} CPUs, {mb_count:2d} motherboards")
    
    # Análisis de RAMs
    print("\n" + "="*60)
    print("🔍 ANÁLISIS DETALLADO: RAMs")
    print("="*60)
    
    rams = by_type['RAM']
    ram_types = defaultdict(int)
    ram_capacities = defaultdict(int)
    
    for ram in rams:
        # Detectar tipo de RAM del nombre
        name = ram['name'].upper()
        if 'DDR5' in name:
            ram_types['DDR5'] += 1
        elif 'DDR4' in name:
            ram_types['DDR4'] += 1
        elif 'DDR3' in name:
            ram_types['DDR3'] += 1
        else:
            ram_types['Unknown'] += 1
        
        # Detectar capacidad
        specs = ram.get('specs', {})
        capacity = specs.get('capacidad', 'Unknown')
        ram_capacities[capacity] += 1
    
    print(f"\n📊 RAMs por tipo:")
    for ram_type, count in sorted(ram_types.items(), key=lambda x: -x[1]):
        print(f"   {ram_type:10s}: {count:2d} módulos")
    
    print(f"\n📊 RAMs por capacidad:")
    for capacity, count in sorted(ram_capacities.items(), key=lambda x: -x[1]):
        print(f"   {capacity:10s}: {count:2d} módulos")
    
    # Análisis de GPUs
    print("\n" + "="*60)
    print("🔍 ANÁLISIS DETALLADO: GPUs")
    print("="*60)
    
    gpus = by_type['GPU']
    gpu_brands = defaultdict(int)
    
    for gpu in gpus:
        name = gpu['name'].upper()
        if 'NVIDIA' in name or 'RTX' in name or 'GTX' in name or 'GEFORCE' in name:
            gpu_brands['NVIDIA'] += 1
        elif 'AMD' in name or 'RADEON' in name or 'RX' in name:
            gpu_brands['AMD'] += 1
        elif 'INTEL' in name or 'ARC' in name:
            gpu_brands['Intel'] += 1
        else:
            gpu_brands['Unknown'] += 1
    
    print(f"\n📊 GPUs por marca:")
    for brand, count in sorted(gpu_brands.items(), key=lambda x: -x[1]):
        print(f"   {brand:10s}: {count:2d} GPUs")
    
    # RECOMENDACIONES
    print("\n" + "="*60)
    print("💡 RECOMENDACIONES")
    print("="*60)
    
    issues = []
    
    if len(motherboards) < 15:
        issues.append(f"⚠️  Solo {len(motherboards)} motherboards (necesitas al menos 15-20)")
    
    # Verificar cobertura de sockets
    uncovered_sockets = []
    for socket in sockets.keys():
        if mb_sockets.get(socket, 0) == 0:
            uncovered_sockets.append(socket)
    
    if uncovered_sockets:
        issues.append(f"⚠️  CPUs sin motherboards compatibles: {', '.join(uncovered_sockets)}")
    
    if issues:
        print("\n❌ PROBLEMAS DETECTADOS:\n")
        for issue in issues:
            print(f"   {issue}")
        
        print("\n📝 ACCIONES NECESARIAS:")
        print("   1. Scrapear más páginas de placas madre en PCFactory")
        print("   2. O agregar motherboards manualmente de otras fuentes")
    else:
        print("\n✅ Dataset completo y balanceado")
    
    print("\n" + "="*60)
    
    return by_type

if __name__ == "__main__":
    analyze_dataset('data/components_20251123_213834.json')