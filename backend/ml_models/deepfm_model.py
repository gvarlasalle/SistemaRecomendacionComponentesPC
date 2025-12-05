# backend/ml_models/deepfm_model.py
"""
Modelo DeepFM (Deep Factorization Machine)
Combina factorización matricial con redes profundas
Alternativa más avanzada al NCF
"""

import torch
import torch.nn as nn


class DeepFMModel(nn.Module):
    """
    Deep Factorization Machine
    Combina FM (factorización) con componente profundo
    """
    
    def __init__(self, num_profiles, num_components, embedding_dim=64, 
                 deep_layers=[128, 64, 32], dropout=0.2):
        super(DeepFMModel, self).__init__()
        
        self.embedding_dim = embedding_dim
        
        # Embeddings para FM
        self.profile_embedding = nn.Embedding(num_profiles, embedding_dim)
        self.component_embedding = nn.Embedding(num_components, embedding_dim)
        
        # Bias terms
        self.profile_bias = nn.Embedding(num_profiles, 1)
        self.component_bias = nn.Embedding(num_components, 1)
        self.global_bias = nn.Parameter(torch.tensor(0.0))
        
        # Componente profundo (MLP)
        deep_layers_list = []
        input_dim = embedding_dim * 2  # Concatenación de ambos embeddings
        
        for hidden_dim in deep_layers:
            deep_layers_list.append(nn.Linear(input_dim, hidden_dim))
            deep_layers_list.append(nn.ReLU())
            deep_layers_list.append(nn.Dropout(dropout))
            input_dim = hidden_dim
        
        # Capa final del deep component
        deep_layers_list.append(nn.Linear(input_dim, 1))
        self.deep_component = nn.Sequential(*deep_layers_list)
        
        # Inicialización
        self._init_weights()
    
    def _init_weights(self):
        """Inicializa pesos"""
        nn.init.normal_(self.profile_embedding.weight, std=0.01)
        nn.init.normal_(self.component_embedding.weight, std=0.01)
        nn.init.zeros_(self.profile_bias.weight)
        nn.init.zeros_(self.component_bias.weight)
        
        for layer in self.deep_component:
            if isinstance(layer, nn.Linear):
                nn.init.xavier_uniform_(layer.weight)
                nn.init.zeros_(layer.bias)
    
    def forward(self, profile_ids, component_ids):
        """
        Forward pass
        Combina FM (factorización) con deep component
        """
        # Obtener embeddings
        profile_emb = self.profile_embedding(profile_ids)
        component_emb = self.component_embedding(component_ids)
        
        # === FM Component (Factorización) ===
        # Producto punto
        fm_dot = (profile_emb * component_emb).sum(dim=1)
        
        # Biases
        profile_b = self.profile_bias(profile_ids).squeeze()
        component_b = self.component_bias(component_ids).squeeze()
        
        fm_output = fm_dot + profile_b + component_b + self.global_bias
        
        # === Deep Component ===
        # Concatenar embeddings
        deep_input = torch.cat([profile_emb, component_emb], dim=-1)
        deep_output = self.deep_component(deep_input).squeeze()
        
        # === Combinar ambos componentes ===
        combined = fm_output + deep_output
        
        # Aplicar sigmoid y escalar a rango [0, 5]
        output = torch.sigmoid(combined) * 5.0
        
        return output

