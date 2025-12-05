# backend/api/recommendation_service.py
"""
Servicio de recomendación que usa múltiples modelos
"""

import torch
import json
from pathlib import Path
from typing import List, Dict
import sys

sys.path.append(str(Path(__file__).parent.parent))

from ml_models.ncf_model import NCFModel
from ml_models.mf_model import MFModel
from ml_models.deepfm_model import DeepFMModel
from ml_models.rule_based_recommender import RuleBasedRecommender

class RecommendationService:
    """Servicio que maneja ambos modelos de recomendación"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / 'data_layer' / 'data'
        self.model_dir = Path(__file__).parent.parent / 'ml_models'
        
        # Cargar componentes y perfiles
        with open(self.data_dir / 'components_normalized.json', 'r', encoding='utf-8') as f:
            self.components = json.load(f)
        
        with open(self.data_dir / 'training_profiles.json', 'r', encoding='utf-8') as f:
            self.profiles = json.load(f)
        
        # Diccionarios para acceso rápido
        self.components_by_id = {c['id']: c for c in self.components}
        self.profiles_by_id = {p['id']: p for p in self.profiles}
        
        # Cargar modelos
        self._load_models()
        
        print("\n✅ Servicio de recomendación inicializado")
        print(f"   Componentes: {len(self.components)}")
        print(f"   Perfiles: {len(self.profiles)}")
    
    def _load_models(self):
        """Carga todos los modelos disponibles"""
        num_profiles = len(self.profiles)
        num_components = len(self.components)
        
        # Modelo basado en reglas (siempre disponible)
        self.rule_model = RuleBasedRecommender(
            components_file=str(self.data_dir / 'components_normalized.json'),
            profiles_file=str(self.data_dir / 'training_profiles.json')
        )
        print("✅ Modelo basado en reglas cargado")
        
        # Modelos neuronales
        self.models = {}
        self.model_mappings = {}
        
        # NCF
        self._load_neural_model('ncf', NCFModel, {
            'embedding_dim': 64,
            'hidden_layers': [128, 64, 32]
        })
        
        # MF
        self._load_neural_model('mf', MFModel, {
            'embedding_dim': 64
        })
        
        # DeepFM
        self._load_neural_model('deepfm', DeepFMModel, {
            'embedding_dim': 64,
            'deep_layers': [128, 64, 32],
            'dropout': 0.2
        })
    
    def _load_neural_model(self, model_name: str, model_class, model_kwargs: Dict):
        """Carga un modelo neuronal"""
        checkpoint_path = self.model_dir / f'{model_name}_model_best.pth'
        
        if not checkpoint_path.exists():
            print(f"⚠️  Modelo {model_name.upper()} no encontrado")
            return
        
        try:
            checkpoint = torch.load(checkpoint_path, map_location='cpu')
            
            num_profiles = len(self.profiles)
            num_components = len(self.components)
            
            model = model_class(
                num_profiles=num_profiles,
                num_components=num_components,
                **model_kwargs
            )
            
            model.load_state_dict(checkpoint['model_state_dict'])
            model.eval()
            
            self.models[model_name] = model
            self.model_mappings[model_name] = {
                'profile_id_to_idx': checkpoint['profile_id_to_idx'],
                'component_id_to_idx': checkpoint['component_id_to_idx']
            }
            
            print(f"✅ Modelo {model_name.upper()} cargado")
        except Exception as e:
            print(f"⚠️  Error cargando modelo {model_name}: {e}")
    
    def predict_neural(self, model_type: str, profile_id: str, component_id: str) -> float:
        """Predice rating con modelo neuronal"""
        if model_type not in self.models:
            return 0.0
        
        model = self.models[model_type]
        mappings = self.model_mappings[model_type]
        
        profile_id_to_idx = mappings['profile_id_to_idx']
        component_id_to_idx = mappings['component_id_to_idx']
        
        if profile_id not in profile_id_to_idx or component_id not in component_id_to_idx:
            return 0.0
        
        profile_idx = profile_id_to_idx[profile_id]
        component_idx = component_id_to_idx[component_id]
        
        with torch.no_grad():
            profile_tensor = torch.tensor([profile_idx], dtype=torch.long)
            component_tensor = torch.tensor([component_idx], dtype=torch.long)
            prediction = model(profile_tensor, component_tensor)
            return float(prediction.item())
    
    def predict_rules(self, profile_id: str, component_id: str) -> float:
        """Predice rating con modelo de reglas"""
        return self.rule_model.predict(profile_id, component_id)
    
    def recommend(self, profile_id: str, model_type: str = 'rule', 
                  top_k: int = 10, component_type: str = None) -> List[Dict]:
        """
        Recomienda componentes para un perfil
        
        Args:
            profile_id: ID del perfil
            model_type: 'ncf' o 'rule'
            top_k: Número de recomendaciones (si es None o muy grande, devuelve todos)
            component_type: Filtrar por tipo (CPU, GPU, etc.)
        """
        profile = self.profiles_by_id.get(profile_id)
        if not profile:
            return []
        
        # Filtrar componentes si se especifica tipo
        components_to_rank = self.components
        if component_type:
            components_to_rank = [c for c in self.components if c['type'] == component_type]
        
        # Si top_k es muy grande (>= 100) o si hay pocos componentes del tipo, calcular scores para todos
        # Esto permite filtrar por compatibilidad primero y luego ordenar
        if top_k >= 100 or top_k >= len(components_to_rank):
            # Calcular scores para todos los componentes del tipo
            scored = []
            for component in components_to_rank:
                if model_type == 'rule':
                    score = self.predict_rules(profile_id, component['id'])
                elif model_type in self.models:
                    score = self.predict_neural(model_type, profile_id, component['id'])
                else:
                    score = self.predict_rules(profile_id, component['id'])
                
                scored.append({
                    'component_id': component['id'],
                    'name': component['name'],
                    'type': component['type'],
                    'brand': component.get('brand', 'Unknown'),
                    'price': component['regular_price'],
                    'predicted_rating': round(score, 2),
                    'features': component.get('features', {}),
                    'url': component.get('url', '')
                })
            
            # Ordenar por score
            scored.sort(key=lambda x: x['predicted_rating'], reverse=True)
            return scored  # Devolver todos si top_k es grande
        else:
            # Para top_k pequeño, comportamiento normal
            scored = []
            for component in components_to_rank:
                if model_type == 'rule':
                    score = self.predict_rules(profile_id, component['id'])
                elif model_type in self.models:
                    score = self.predict_neural(model_type, profile_id, component['id'])
                else:
                    score = self.predict_rules(profile_id, component['id'])
                
                scored.append({
                    'component_id': component['id'],
                    'name': component['name'],
                    'type': component['type'],
                    'brand': component.get('brand', 'Unknown'),
                    'price': component['regular_price'],
                    'predicted_rating': round(score, 2),
                    'features': component.get('features', {}),
                    'url': component.get('url', '')
                })
            
            # Ordenar por score
            scored.sort(key=lambda x: x['predicted_rating'], reverse=True)
            return scored[:top_k]
    
    def get_profile_info(self, profile_id: str) -> Dict:
        """Obtiene información de un perfil"""
        return self.profiles_by_id.get(profile_id, {})
    
    def list_profiles(self) -> List[Dict]:
        """Lista todos los perfiles disponibles"""
        return [
            {
                'id': p['id'],
                'name': p['name'],
                'budget_range': p['budget_range'],
                'priority_components': p['priority_components']
            }
            for p in self.profiles
        ]

# ==================== TEST ====================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TEST DEL SERVICIO DE RECOMENDACIÓN")
    print("="*60)
    
    service = RecommendationService()
    
    # Test con perfil Gamer Medio
    profile_id = 'gamer_mid'
    
    print(f"\n📊 Recomendaciones para: {profile_id}")
    print("="*60)
    
    # GPU recommendations con NCF
    print("\n🎮 Top 5 GPUs (Modelo NCF):")
    gpu_recs_ncf = service.recommend(profile_id, model_type='ncf', top_k=5, component_type='GPU')
    for i, rec in enumerate(gpu_recs_ncf, 1):
        print(f"   {i}. {rec['name'][:50]}")
        print(f"      Rating: {rec['predicted_rating']:.2f} | Precio: S/ {rec['price']}")
    
    # GPU recommendations con Rules
    print("\n🎮 Top 5 GPUs (Modelo Reglas):")
    gpu_recs_rule = service.recommend(profile_id, model_type='rule', top_k=5, component_type='GPU')
    for i, rec in enumerate(gpu_recs_rule, 1):
        print(f"   {i}. {rec['name'][:50]}")
        print(f"      Rating: {rec['predicted_rating']:.2f} | Precio: S/ {rec['price']}")
    
    print("\n" + "="*60)