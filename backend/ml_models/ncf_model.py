# backend/ml_models/ncf_model.py
"""
Modelo Neural Collaborative Filtering (NCF)
Para recomendación de componentes PC basado en perfiles
"""

import torch
import torch.nn as nn

class NCFModel(nn.Module):
    """
    Neural Collaborative Filtering
    Profile-Component en lugar de User-Item tradicional
    """
    def __init__(self, num_profiles, num_components, embedding_dim=64, hidden_layers=[128, 64, 32]):
        super(NCFModel, self).__init__()
        
        # Embeddings
        self.profile_embedding = nn.Embedding(num_profiles, embedding_dim)
        self.component_embedding = nn.Embedding(num_components, embedding_dim)
        
        # MLP (Multi-Layer Perceptron)
        layers = []
        input_dim = embedding_dim * 2
        
        for hidden_dim in hidden_layers:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.2))
            input_dim = hidden_dim
        
        # Capa final (output: rating predicho)
        layers.append(nn.Linear(input_dim, 1))
        
        self.mlp = nn.Sequential(*layers)
        
        # Inicialización de pesos
        self._init_weights()
    
    def _init_weights(self):
        """Inicializa pesos con distribución normal"""
        nn.init.normal_(self.profile_embedding.weight, std=0.01)
        nn.init.normal_(self.component_embedding.weight, std=0.01)
        
        for layer in self.mlp:
            if isinstance(layer, nn.Linear):
                nn.init.xavier_uniform_(layer.weight)
                nn.init.zeros_(layer.bias)
    
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
        profile_embedded = self.profile_embedding(profile_ids)
        component_embedded = self.component_embedding(component_ids)
        
        # Concatenar embeddings
        x = torch.cat([profile_embedded, component_embedded], dim=-1)
        
        # Pasar por MLP
        output = self.mlp(x)
        
        # Aplicar sigmoid y escalar a rango [0, 5]
        output = torch.sigmoid(output) * 5.0
        
        return output.squeeze()