# backend/ml_models/mf_model.py
"""
Modelo Matrix Factorization (MF)
Alternativa más simple al NCF para comparación
"""

import torch
import torch.nn as nn
import numpy as np


class MFModel(nn.Module):
    """
    Matrix Factorization tradicional
    Factoriza la matriz perfil-componente en dos matrices de embeddings
    """
    
    def __init__(self, num_profiles, num_components, embedding_dim=64):
        super(MFModel, self).__init__()
        
        # Embeddings para perfiles y componentes
        self.profile_embedding = nn.Embedding(num_profiles, embedding_dim)
        self.component_embedding = nn.Embedding(num_components, embedding_dim)
        
        # Bias terms
        self.profile_bias = nn.Embedding(num_profiles, 1)
        self.component_bias = nn.Embedding(num_components, 1)
        
        # Bias global
        self.global_bias = nn.Parameter(torch.tensor(0.0))
        
        # Inicialización
        self._init_weights()
    
    def _init_weights(self):
        """Inicializa pesos con distribución normal"""
        nn.init.normal_(self.profile_embedding.weight, std=0.01)
        nn.init.normal_(self.component_embedding.weight, std=0.01)
        nn.init.zeros_(self.profile_bias.weight)
        nn.init.zeros_(self.component_bias.weight)
    
    def forward(self, profile_ids, component_ids):
        """
        Forward pass
        Args:
            profile_ids: tensor de IDs de perfiles
            component_ids: tensor de IDs de componentes
        Returns:
            ratings predichos (0-5)
        """
        # Obtener embeddings
        profile_emb = self.profile_embedding(profile_ids)
        component_emb = self.component_embedding(component_ids)
        
        # Producto punto (dot product)
        dot_product = (profile_emb * component_emb).sum(dim=1)
        
        # Agregar biases
        profile_b = self.profile_bias(profile_ids).squeeze()
        component_b = self.component_bias(component_ids).squeeze()
        
        # Predicción
        output = dot_product + profile_b + component_b + self.global_bias
        
        # Aplicar sigmoid y escalar a rango [0, 5]
        output = torch.sigmoid(output) * 5.0
        
        return output

