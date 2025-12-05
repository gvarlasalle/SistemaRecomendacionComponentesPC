# backend/ml_models/model_evaluator.py
"""
Sistema de evaluación para comparar modelos de recomendación
Calcula métricas: RMSE, MAE, Precision@K, Recall@K, NDCG
"""

import json
import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import sys

sys.path.append(str(Path(__file__).parent.parent))

from ml_models.ncf_model import NCFModel
from ml_models.mf_model import MFModel
from ml_models.deepfm_model import DeepFMModel
from ml_models.rule_based_recommender import RuleBasedRecommender


class ModelEvaluator:
    """Evalúa y compara modelos de recomendación"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / 'data_layer' / 'data'
        self.model_dir = Path(__file__).parent.parent / 'ml_models'
        
        # Cargar datos
        with open(self.data_dir / 'components_normalized.json', 'r', encoding='utf-8') as f:
            self.components = json.load(f)
        
        with open(self.data_dir / 'training_profiles.json', 'r', encoding='utf-8') as f:
            self.profiles = json.load(f)
        
        with open(self.data_dir / 'training_interactions.json', 'r', encoding='utf-8') as f:
            self.interactions = json.load(f)
        
        self.components_by_id = {c['id']: c for c in self.components}
        self.profiles_by_id = {p['id']: p for p in self.profiles}
    
    def load_model(self, model_type: str):
        """Carga un modelo según su tipo"""
        if model_type == 'rule':
            return RuleBasedRecommender(
                components_file=str(self.data_dir / 'components_normalized.json'),
                profiles_file=str(self.data_dir / 'training_profiles.json')
            )
        
        # Modelos neuronales
        checkpoint_path = self.model_dir / f'{model_type}_model_best.pth'
        
        if not checkpoint_path.exists():
            return None
        
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        
        num_profiles = len(self.profiles)
        num_components = len(self.components)
        
        if model_type == 'ncf':
            model = NCFModel(
                num_profiles=num_profiles,
                num_components=num_components,
                embedding_dim=64,
                hidden_layers=[128, 64, 32]
            )
        elif model_type == 'mf':
            model = MFModel(
                num_profiles=num_profiles,
                num_components=num_components,
                embedding_dim=64
            )
        elif model_type == 'deepfm':
            model = DeepFMModel(
                num_profiles=num_profiles,
                num_components=num_components,
                embedding_dim=64,
                deep_layers=[128, 64, 32]
            )
        else:
            return None
        
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()
        
        return {
            'model': model,
            'profile_id_to_idx': checkpoint['profile_id_to_idx'],
            'component_id_to_idx': checkpoint['component_id_to_idx']
        }
    
    def predict_rating(self, model_obj, profile_id: str, component_id: str) -> float:
        """Predice rating para un par perfil-componente"""
        if isinstance(model_obj, RuleBasedRecommender):
            return model_obj.predict(profile_id, component_id)
        
        # Modelo neuronal
        model = model_obj['model']
        profile_id_to_idx = model_obj['profile_id_to_idx']
        component_id_to_idx = model_obj['component_id_to_idx']
        
        if profile_id not in profile_id_to_idx or component_id not in component_id_to_idx:
            return 0.0
        
        profile_idx = profile_id_to_idx[profile_id]
        component_idx = component_id_to_idx[component_id]
        
        with torch.no_grad():
            profile_tensor = torch.tensor([profile_idx], dtype=torch.long)
            component_tensor = torch.tensor([component_idx], dtype=torch.long)
            prediction = model(profile_tensor, component_tensor)
            return float(prediction.item())
    
    def evaluate_rating_metrics(self, model_obj, test_interactions: List[Dict]) -> Dict:
        """Evalúa métricas de rating (RMSE, MAE)"""
        errors = []
        absolute_errors = []
        
        for interaction in test_interactions:
            profile_id = interaction['profile_id']
            component_id = interaction['component_id']
            true_rating = interaction['rating']
            
            predicted_rating = self.predict_rating(model_obj, profile_id, component_id)
            
            error = predicted_rating - true_rating
            errors.append(error ** 2)
            absolute_errors.append(abs(error))
        
        mse = np.mean(errors)
        mae = np.mean(absolute_errors)
        rmse = np.sqrt(mse)
        
        return {
            'mse': float(mse),
            'mae': float(mae),
            'rmse': float(rmse)
        }
    
    def evaluate_ranking_metrics(self, model_obj, k: int = 10) -> Dict:
        """Evalúa métricas de ranking (Precision@K, Recall@K, NDCG@K)"""
        # Agrupar interacciones por perfil
        profile_interactions = {}
        for interaction in self.interactions:
            profile_id = interaction['profile_id']
            if profile_id not in profile_interactions:
                profile_interactions[profile_id] = []
            profile_interactions[profile_id].append(interaction)
        
        precisions = []
        recalls = []
        ndcgs = []
        
        for profile_id, interactions in list(profile_interactions.items())[:50]:  # Limitar para velocidad
            # Obtener componentes relevantes (con rating >= 4.0)
            relevant_components = {
                i['component_id'] for i in interactions if i['rating'] >= 4.0
            }
            
            if not relevant_components:
                continue
            
            # Predecir ratings para todos los componentes
            component_scores = []
            for component in self.components:
                score = self.predict_rating(model_obj, profile_id, component['id'])
                component_scores.append((component['id'], score))
            
            # Ordenar y tomar top-k
            component_scores.sort(key=lambda x: x[1], reverse=True)
            top_k_components = {comp_id for comp_id, _ in component_scores[:k]}
            
            # Precision@K
            if len(top_k_components) > 0:
                precision = len(relevant_components & top_k_components) / len(top_k_components)
                precisions.append(precision)
            
            # Recall@K
            recall = len(relevant_components & top_k_components) / len(relevant_components)
            recalls.append(recall)
            
            # NDCG@K
            dcg = 0.0
            for i, (comp_id, score) in enumerate(component_scores[:k]):
                if comp_id in relevant_components:
                    dcg += 1.0 / np.log2(i + 2)
            
            idcg = sum(1.0 / np.log2(i + 2) for i in range(min(k, len(relevant_components))))
            ndcg = dcg / idcg if idcg > 0 else 0.0
            ndcgs.append(ndcg)
        
        return {
            'precision@k': float(np.mean(precisions)) if precisions else 0.0,
            'recall@k': float(np.mean(recalls)) if recalls else 0.0,
            'ndcg@k': float(np.mean(ndcgs)) if ndcgs else 0.0
        }
    
    def evaluate_model(self, model_type: str) -> Dict:
        """Evalúa un modelo completo"""
        print(f"\n📊 Evaluando modelo: {model_type}")
        
        # Cargar modelo
        model_obj = self.load_model(model_type)
        if model_obj is None:
            return None
        
        # Split train/test (80/20)
        test_size = int(0.2 * len(self.interactions))
        test_interactions = self.interactions[-test_size:]
        
        # Métricas de rating
        rating_metrics = self.evaluate_rating_metrics(model_obj, test_interactions)
        
        # Métricas de ranking
        ranking_metrics = self.evaluate_ranking_metrics(model_obj, k=10)
        
        return {
            'model_type': model_type,
            'rating_metrics': rating_metrics,
            'ranking_metrics': ranking_metrics
        }
    
    def compare_all_models(self) -> Dict:
        """Compara todos los modelos disponibles"""
        print("\n" + "="*60)
        print("🔬 COMPARACIÓN DE MODELOS DE RECOMENDACIÓN")
        print("="*60)
        
        model_types = ['rule', 'ncf', 'mf', 'deepfm']
        results = {}
        
        for model_type in model_types:
            result = self.evaluate_model(model_type)
            if result:
                results[model_type] = result
        
        # Imprimir resultados
        print("\n" + "="*60)
        print("📊 RESULTADOS DE EVALUACIÓN")
        print("="*60)
        
        for model_type, result in results.items():
            print(f"\n{model_type.upper()}:")
            print(f"  Rating Metrics:")
            print(f"    RMSE: {result['rating_metrics']['rmse']:.4f}")
            print(f"    MAE:  {result['rating_metrics']['mae']:.4f}")
            print(f"  Ranking Metrics:")
            print(f"    Precision@10: {result['ranking_metrics']['precision@k']:.4f}")
            print(f"    Recall@10:    {result['ranking_metrics']['recall@k']:.4f}")
            print(f"    NDCG@10:      {result['ranking_metrics']['ndcg@k']:.4f}")
        
        # Determinar mejor modelo
        best_model = self._select_best_model(results)
        
        print("\n" + "="*60)
        print(f"🏆 MEJOR MODELO: {best_model.upper()}")
        print("="*60)
        
        return {
            'results': results,
            'best_model': best_model
        }
    
    def _select_best_model(self, results: Dict) -> str:
        """Selecciona el mejor modelo basado en métricas combinadas"""
        if not results:
            return None
        
        scores = {}
        
        for model_type, result in results.items():
            # Score combinado: menor RMSE es mejor, mayor NDCG es mejor
            rmse = result['rating_metrics']['rmse']
            ndcg = result['ranking_metrics']['ndcg@k']
            
            # Normalizar y combinar (peso 0.4 para RMSE, 0.6 para NDCG)
            # Invertir RMSE para que mayor sea mejor
            max_rmse = max(r['rating_metrics']['rmse'] for r in results.values())
            normalized_rmse = 1.0 - (rmse / max_rmse) if max_rmse > 0 else 0.0
            
            score = 0.4 * normalized_rmse + 0.6 * ndcg
            scores[model_type] = score
        
        return max(scores, key=scores.get)


if __name__ == "__main__":
    evaluator = ModelEvaluator()
    comparison = evaluator.compare_all_models()
    
    # Guardar resultados
    output_path = Path(__file__).parent / 'model_comparison_results.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2)
    
    print(f"\n💾 Resultados guardados en: {output_path}")

