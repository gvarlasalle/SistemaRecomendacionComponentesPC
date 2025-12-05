# backend/ml_models/rule_based_recommender.py
"""
Modelo de recomendación basado en reglas y features
Sin redes neuronales - solo lógica de compatibilidad y scoring
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List

class RuleBasedRecommender:
    """
    Recomendador basado en reglas de compatibilidad y scoring de features
    Más simple que NCF, sirve como baseline de comparación
    """
    
    def __init__(self, components_file: str, profiles_file: str):
        # Cargar datos
        with open(components_file, 'r', encoding='utf-8') as f:
            self.components = json.load(f)
        
        with open(profiles_file, 'r', encoding='utf-8') as f:
            self.profiles = json.load(f)
        
        # Crear diccionario por ID
        self.components_by_id = {c['id']: c for c in self.components}
        self.profiles_by_id = {p['id']: p for p in self.profiles}
        
        print(f"\n📊 Recomendador basado en reglas inicializado:")
        print(f"   Componentes: {len(self.components)}")
        print(f"   Perfiles: {len(self.profiles)}")
    
    def calculate_feature_score(self, profile: Dict, component: Dict) -> float:
        """
        Calcula score basado en features técnicos
        Similar al sistema de ratings sintéticos pero más detallado
        """
        comp_type = component['type']
        features = component.get('features', {})
        price = component.get('regular_price', 0)
        
        requirements = profile['requirements'].get(comp_type, {})
        if not requirements:
            return 3.0
        
        # Componente opcional
        if requirements.get('optional', False):
            if comp_type not in profile['priority_components']:
                return 2.5
        
        score = 5.0
        
        # === CPU ===
        if comp_type == 'CPU':
            cores = features.get('cores', 0)
            tier = features.get('performance_tier', '')
            freq = features.get('base_frequency_ghz', 0)
            has_igpu = features.get('has_integrated_gpu', False)
            
            # Cores
            cores_min = requirements.get('cores_min', 0)
            if cores < cores_min:
                score -= 2.5
            elif cores == cores_min:
                score -= 0.3
            elif cores > cores_min * 1.5:
                score += 0.3  # Bonus por muchos cores
            
            # Tier
            tier_req = requirements.get('performance_tier', [])
            if tier_req and tier not in tier_req:
                score -= 2.0
            
            # Frecuencia (bonus)
            if freq >= 4.0:
                score += 0.2
            
            # iGPU
            if requirements.get('has_igpu', False) and not has_igpu:
                score -= 1.5
        
        # === GPU ===
        elif comp_type == 'GPU':
            vram = features.get('vram_gb', 0)
            tier = features.get('performance_tier', '')
            
            # VRAM
            vram_min = requirements.get('vram_min', 0)
            if vram < vram_min:
                score -= 2.5
            elif vram >= vram_min * 1.5:
                score += 0.3  # Bonus por mucha VRAM
            
            # Tier
            tier_req = requirements.get('performance_tier', [])
            if tier_req and tier not in tier_req:
                score -= 2.0
        
        # === RAM ===
        elif comp_type == 'RAM':
            capacity = features.get('capacity_gb', 0)
            ram_type = features.get('ram_type', '')
            frequency = features.get('frequency_mhz', 0)
            
            # Capacidad
            capacity_min = requirements.get('capacity_min', 0)
            if capacity < capacity_min:
                score -= 2.5
            elif capacity == capacity_min:
                score -= 0.2
            elif capacity > capacity_min * 1.5:
                score += 0.3
            
            # Tipo
            type_req = requirements.get('type', [])
            if type_req and ram_type not in type_req:
                score -= 1.5
            
            # Frecuencia (bonus)
            if frequency >= 3600:
                score += 0.2
        
        # === STORAGE ===
        elif comp_type == 'STORAGE':
            capacity = features.get('capacity_gb', 0)
            storage_type = features.get('storage_type', '')
            
            # Capacidad
            capacity_min = requirements.get('capacity_min', 0)
            if capacity < capacity_min:
                score -= 2.5
            elif capacity > capacity_min * 2:
                score += 0.3
            
            # Tipo
            type_req = requirements.get('type', [])
            if type_req and storage_type not in type_req:
                score -= 1.5
            
            # Bonus por NVME
            if storage_type == 'NVME':
                score += 0.2
        
        # === PSU ===
        elif comp_type == 'PSU':
            wattage = features.get('wattage', 0)
            efficiency = features.get('efficiency_rating', '')
            is_modular = features.get('is_modular', False)
            
            # Wattage
            wattage_min = requirements.get('wattage_min', 0)
            if wattage < wattage_min:
                score -= 3.0
            elif wattage < wattage_min * 1.15:
                score -= 0.5
            elif wattage > wattage_min * 1.5:
                score += 0.2
            
            # Eficiencia (bonus)
            if 'Gold' in efficiency or 'Platinum' in efficiency:
                score += 0.3
            
            # Modular (bonus)
            if is_modular:
                score += 0.2
        
        # === MOTHERBOARD ===
        elif comp_type == 'MOTHERBOARD':
            price_max = requirements.get('price_max', 999999)
            if price > price_max:
                score -= 2.0
            elif price < price_max * 0.5:
                score += 0.2  # Bonus por precio bajo
        
        # === Penalización por presupuesto ===
        budget_min, budget_max = profile['budget_range']
        max_component_price = budget_max * 0.45
        
        if price > max_component_price:
            score -= 1.5
        elif price < max_component_price * 0.3:
            score += 0.3  # Bonus por buen precio
        
        # === Bonus por prioridad ===
        if comp_type in profile['priority_components']:
            score += 0.5
        
        # Clamp a rango [0, 5]
        score = max(0.0, min(5.0, score))
        return round(score, 2)
    
    def predict(self, profile_id: str, component_id: str) -> float:
        """Predice rating para un par perfil-componente"""
        profile = self.profiles_by_id.get(profile_id)
        component = self.components_by_id.get(component_id)
        
        if not profile or not component:
            return 0.0
        
        return self.calculate_feature_score(profile, component)
    
    def recommend_for_profile(self, profile_id: str, top_k: int = 10) -> List[Dict]:
        """Recomienda top-k componentes para un perfil"""
        profile = self.profiles_by_id.get(profile_id)
        if not profile:
            return []
        
        # Calcular scores para todos los componentes
        scored_components = []
        for component in self.components:
            score = self.calculate_feature_score(profile, component)
            scored_components.append({
                'component_id': component['id'],
                'component_name': component['name'],
                'component_type': component['type'],
                'component_price': component['regular_price'],
                'predicted_rating': score
            })
        
        # Ordenar por score descendente
        scored_components.sort(key=lambda x: x['predicted_rating'], reverse=True)
        
        return scored_components[:top_k]
    
    def save_model(self, output_path: str):
        """Guarda el modelo (solo metadata, no hay pesos)"""
        model_info = {
            'model_type': 'RuleBasedRecommender',
            'num_components': len(self.components),
            'num_profiles': len(self.profiles),
            'description': 'Recomendador basado en reglas de compatibilidad y scoring de features'
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(model_info, f, indent=2)
        
        print(f"\n💾 Metadata del modelo guardada en: {output_path}")

# ==================== EVALUACIÓN ====================

def evaluate_rule_based():
    """Evalúa el modelo basado en reglas"""
    
    print("\n" + "="*60)
    print("📊 EVALUACIÓN MODELO BASADO EN REGLAS")
    print("="*60)
    
    # Paths
    data_dir = Path(__file__).parent.parent / 'data_layer' / 'data'
    components_file = data_dir / 'components_normalized.json'
    profiles_file = data_dir / 'training_profiles.json'
    interactions_file = data_dir / 'training_interactions.json'
    
    # Cargar modelo
    model = RuleBasedRecommender(
        components_file=str(components_file),
        profiles_file=str(profiles_file)
    )
    
    # Cargar interacciones para evaluar
    with open(interactions_file, 'r', encoding='utf-8') as f:
        interactions = json.load(f)
    
    print(f"\n🔄 Evaluando en {len(interactions)} interacciones...")
    
    # Calcular MSE y MAE
    errors = []
    absolute_errors = []
    
    for interaction in interactions:
        profile_id = interaction['profile_id']
        component_id = interaction['component_id']
        true_rating = interaction['rating']
        
        predicted_rating = model.predict(profile_id, component_id)
        
        error = predicted_rating - true_rating
        errors.append(error ** 2)  # MSE
        absolute_errors.append(abs(error))  # MAE
    
    mse = np.mean(errors)
    mae = np.mean(absolute_errors)
    rmse = np.sqrt(mse)
    
    print(f"\n📊 Métricas:")
    print(f"   MSE:  {mse:.4f}")
    print(f"   RMSE: {rmse:.4f}")
    print(f"   MAE:  {mae:.4f}")
    
    # Guardar metadata
    model_path = Path(__file__).parent / 'rule_based_model_metadata.json'
    model.save_model(str(model_path))
    
    print("\n" + "="*60)
    print("✅ EVALUACIÓN COMPLETADA")
    print("="*60 + "\n")
    
    return {'mse': mse, 'rmse': rmse, 'mae': mae}

if __name__ == "__main__":
    evaluate_rule_based()