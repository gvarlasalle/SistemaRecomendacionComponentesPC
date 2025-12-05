# backend/data_layer/generate_training_data.py
"""
Genera dataset de entrenamiento para modelo NCF
- Crea perfiles sintéticos de usuarios
- Genera interacciones (perfil → componente → rating)
"""

import json
import random
from collections import defaultdict

# ==================== PERFILES SINTÉTICOS ====================

PROFILES = [
    {
        'id': 'gamer_budget',
        'name': 'Gamer Presupuesto',
        'budget_range': (1000, 1500),
        'priority_components': ['GPU', 'CPU'],
        'requirements': {
            'GPU': {'performance_tier': ['budget', 'mid'], 'vram_min': 4},
            'CPU': {'cores_min': 4, 'performance_tier': ['budget', 'mid']},
            'RAM': {'capacity_min': 8, 'type': ['DDR4', 'DDR5']},
            'STORAGE': {'capacity_min': 256, 'type': ['SSD', 'NVME']},
            'PSU': {'wattage_min': 450},
            'MOTHERBOARD': {'price_max': 600}
        }
    },
    {
        'id': 'gamer_mid',
        'name': 'Gamer Medio',
        'budget_range': (1500, 2500),
        'priority_components': ['GPU', 'CPU'],
        'requirements': {
            'GPU': {'performance_tier': ['mid', 'high'], 'vram_min': 8},
            'CPU': {'cores_min': 6, 'performance_tier': ['mid', 'high']},
            'RAM': {'capacity_min': 16, 'type': ['DDR4', 'DDR5']},
            'STORAGE': {'capacity_min': 500, 'type': ['NVME']},
            'PSU': {'wattage_min': 550},
            'MOTHERBOARD': {'price_max': 1000}
        }
    },
    {
        'id': 'gamer_high',
        'name': 'Gamer Alto',
        'budget_range': (2500, 4000),
        'priority_components': ['GPU', 'CPU'],
        'requirements': {
            'GPU': {'performance_tier': ['high', 'enthusiast'], 'vram_min': 12},
            'CPU': {'cores_min': 8, 'performance_tier': ['high', 'enthusiast']},
            'RAM': {'capacity_min': 16, 'type': ['DDR5']},
            'STORAGE': {'capacity_min': 1000, 'type': ['NVME']},
            'PSU': {'wattage_min': 650},
            'MOTHERBOARD': {'price_max': 1500}
        }
    },
    {
        'id': 'developer_budget',
        'name': 'Desarrollador Presupuesto',
        'budget_range': (800, 1200),
        'priority_components': ['CPU', 'RAM', 'STORAGE'],
        'requirements': {
            'CPU': {'cores_min': 4, 'performance_tier': ['budget', 'mid']},
            'RAM': {'capacity_min': 16, 'type': ['DDR4', 'DDR5']},
            'STORAGE': {'capacity_min': 500, 'type': ['SSD', 'NVME']},
            'GPU': {'optional': True},
            'PSU': {'wattage_min': 400},
            'MOTHERBOARD': {'price_max': 600}
        }
    },
    {
        'id': 'developer_mid',
        'name': 'Desarrollador Medio',
        'budget_range': (1500, 2500),
        'priority_components': ['CPU', 'RAM', 'STORAGE'],
        'requirements': {
            'CPU': {'cores_min': 8, 'performance_tier': ['mid', 'high']},
            'RAM': {'capacity_min': 32, 'type': ['DDR4', 'DDR5']},
            'STORAGE': {'capacity_min': 1000, 'type': ['NVME']},
            'GPU': {'optional': True, 'performance_tier': ['budget', 'mid']},
            'PSU': {'wattage_min': 500},
            'MOTHERBOARD': {'price_max': 1000}
        }
    },
    {
        'id': 'designer_mid',
        'name': 'Diseñador Medio',
        'budget_range': (1800, 2800),
        'priority_components': ['GPU', 'CPU', 'RAM'],
        'requirements': {
            'GPU': {'performance_tier': ['mid', 'high'], 'vram_min': 8},
            'CPU': {'cores_min': 8, 'performance_tier': ['mid', 'high']},
            'RAM': {'capacity_min': 32, 'type': ['DDR4', 'DDR5']},
            'STORAGE': {'capacity_min': 1000, 'type': ['NVME']},
            'PSU': {'wattage_min': 550},
            'MOTHERBOARD': {'price_max': 1200}
        }
    },
    {
        'id': 'designer_high',
        'name': 'Diseñador Alto',
        'budget_range': (3000, 5000),
        'priority_components': ['GPU', 'CPU', 'RAM'],
        'requirements': {
            'GPU': {'performance_tier': ['high', 'enthusiast'], 'vram_min': 12},
            'CPU': {'cores_min': 12, 'performance_tier': ['high', 'enthusiast']},
            'RAM': {'capacity_min': 32, 'type': ['DDR5']},
            'STORAGE': {'capacity_min': 2000, 'type': ['NVME']},
            'PSU': {'wattage_min': 750},
            'MOTHERBOARD': {'price_max': 2000}
        }
    },
    {
        'id': 'office_budget',
        'name': 'Oficina Presupuesto',
        'budget_range': (500, 900),
        'priority_components': ['CPU', 'RAM'],
        'requirements': {
            'CPU': {'cores_min': 2, 'performance_tier': ['budget'], 'has_igpu': True},
            'RAM': {'capacity_min': 8, 'type': ['DDR4']},
            'STORAGE': {'capacity_min': 256, 'type': ['SSD']},
            'GPU': {'optional': True},
            'PSU': {'wattage_min': 350},
            'MOTHERBOARD': {'price_max': 400}
        }
    },
    {
        'id': 'student_budget',
        'name': 'Estudiante Presupuesto',
        'budget_range': (600, 1100),
        'priority_components': ['CPU', 'RAM'],
        'requirements': {
            'CPU': {'cores_min': 4, 'performance_tier': ['budget', 'mid']},
            'RAM': {'capacity_min': 8, 'type': ['DDR4']},
            'STORAGE': {'capacity_min': 256, 'type': ['SSD']},
            'GPU': {'optional': True, 'performance_tier': ['budget']},
            'PSU': {'wattage_min': 400},
            'MOTHERBOARD': {'price_max': 500}
        }
    }
]

# ==================== CÁLCULO DE RATING ====================

def calculate_component_rating(profile, component):
    """Calcula qué tan bien encaja un componente con un perfil"""
    comp_type = component['type']
    features = component.get('features', {})
    price = component.get('regular_price', 0)
    
    requirements = profile['requirements'].get(comp_type, {})
    if not requirements:
        return 3.0
    
    if requirements.get('optional', False):
        if comp_type not in profile['priority_components']:
            return 2.5
    
    rating = 5.0
    
    # CPU
    if comp_type == 'CPU':
        cores = features.get('cores', 0)
        tier = features.get('performance_tier', '')
        has_igpu = features.get('has_integrated_gpu', False)
        
        cores_min = requirements.get('cores_min', 0)
        if cores < cores_min:
            rating -= 2.0
        elif cores == cores_min:
            rating -= 0.5
        
        tier_req = requirements.get('performance_tier', [])
        if tier_req and tier not in tier_req:
            rating -= 1.5
        
        if requirements.get('has_igpu', False) and not has_igpu:
            rating -= 1.0
    
    # GPU
    elif comp_type == 'GPU':
        vram = features.get('vram_gb', 0)
        tier = features.get('performance_tier', '')
        
        vram_min = requirements.get('vram_min', 0)
        if vram < vram_min:
            rating -= 2.0
        
        tier_req = requirements.get('performance_tier', [])
        if tier_req and tier not in tier_req:
            rating -= 1.5
    
    # RAM
    elif comp_type == 'RAM':
        capacity = features.get('capacity_gb', 0)
        ram_type = features.get('ram_type', '')
        
        capacity_min = requirements.get('capacity_min', 0)
        if capacity < capacity_min:
            rating -= 2.0
        elif capacity == capacity_min:
            rating -= 0.3
        
        type_req = requirements.get('type', [])
        if type_req and ram_type not in type_req:
            rating -= 1.0
    
    # STORAGE
    elif comp_type == 'STORAGE':
        capacity = features.get('capacity_gb', 0)
        storage_type = features.get('storage_type', '')
        
        capacity_min = requirements.get('capacity_min', 0)
        if capacity < capacity_min:
            rating -= 2.0
        
        type_req = requirements.get('type', [])
        if type_req and storage_type not in type_req:
            rating -= 1.0
    
    # PSU
    elif comp_type == 'PSU':
        wattage = features.get('wattage', 0)
        
        wattage_min = requirements.get('wattage_min', 0)
        if wattage < wattage_min:
            rating -= 2.5
        elif wattage < wattage_min * 1.2:
            rating -= 0.5
    
    # MOTHERBOARD
    elif comp_type == 'MOTHERBOARD':
        price_max = requirements.get('price_max', 999999)
        if price > price_max:
            rating -= 1.5
    
    # Penalización por precio
    budget_min, budget_max = profile['budget_range']
    max_component_price = budget_max * 0.4
    
    if price > max_component_price:
        rating -= 1.0
    
    # Bonus por prioridad
    if comp_type in profile['priority_components']:
        rating += 0.5
    
    rating = max(0.0, min(5.0, rating))
    return round(rating, 2)

# ==================== GENERACIÓN ====================

def generate_interactions(components, profiles, interactions_per_profile=80):
    """Genera interacciones sintéticas"""
    interactions = []
    
    by_type = defaultdict(list)
    for comp in components:
        by_type[comp['type']].append(comp)
    
    print(f"\n📊 Componentes por tipo:")
    for comp_type, comps in sorted(by_type.items()):
        print(f"   {comp_type:15s}: {len(comps):3d}")
    
    print(f"\n🔄 Generando interacciones...")
    
    for profile in profiles:
        profile_interactions = []
        
        for comp_type, comps in by_type.items():
            num_interactions = min(len(comps), interactions_per_profile // len(by_type))
            selected = random.sample(comps, num_interactions)
            
            for comp in selected:
                rating = calculate_component_rating(profile, comp)
                
                interaction = {
                    'profile_id': profile['id'],
                    'profile_name': profile['name'],
                    'component_id': comp['id'],
                    'component_name': comp['name'],
                    'component_type': comp['type'],
                    'component_price': comp['regular_price'],
                    'rating': rating
                }
                
                profile_interactions.append(interaction)
        
        interactions.extend(profile_interactions)
        print(f"   ✅ {profile['name']:30s}: {len(profile_interactions):4d} interacciones")
    
    return interactions

# ==================== MAIN ====================

def generate_training_dataset(components_file, output_file):
    """Genera dataset completo"""
    
    print("\n" + "="*60)
    print("🎲 GENERANDO DATASET DE ENTRENAMIENTO")
    print("="*60)
    
    with open(components_file, 'r', encoding='utf-8') as f:
        components = json.load(f)
    
    print(f"\n📦 Componentes cargados: {len(components)}")
    print(f"👥 Perfiles definidos: {len(PROFILES)}")
    
    interactions = generate_interactions(components, PROFILES, interactions_per_profile=80)
    
    print(f"\n📊 Interacciones generadas: {len(interactions)}")
    
    # Distribución de ratings
    rating_dist = defaultdict(int)
    for inter in interactions:
        rating_bucket = int(inter['rating'])
        rating_dist[rating_bucket] += 1
    
    print(f"\n📈 Distribución de ratings:")
    for rating in sorted(rating_dist.keys()):
        count = rating_dist[rating]
        bar = "█" * (count // 50)
        print(f"   {rating} estrellas: {count:4d} {bar}")
    
    # Guardar
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(interactions, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Dataset guardado: {output_file}")
    
    # Guardar perfiles
    profiles_file = output_file.replace('interactions', 'profiles')
    with open(profiles_file, 'w', encoding='utf-8') as f:
        json.dump(PROFILES, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Perfiles guardados: {profiles_file}")
    
    print("\n" + "="*60)
    print("✅ DATASET DE ENTRENAMIENTO LISTO")
    print("="*60)
    
    return interactions

if __name__ == "__main__":
    generate_training_dataset(
        components_file='data/components_normalized.json',
        output_file='data/training_interactions.json'
    )