# backend/ml_models/train_ncf.py
"""
Entrena el modelo NCF con las interacciones sintéticas
"""

import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from pathlib import Path
import sys

# Agregar path del proyecto
sys.path.append(str(Path(__file__).parent.parent))

from ml_models.ncf_model import NCFModel

# ==================== DATASET ====================

class ComponentInteractionDataset(Dataset):
    """Dataset de interacciones perfil-componente"""
    
    def __init__(self, interactions_file, profiles_file, components_file):
        # Cargar datos
        with open(interactions_file, 'r', encoding='utf-8') as f:
            self.interactions = json.load(f)
        
        with open(profiles_file, 'r', encoding='utf-8') as f:
            self.profiles = json.load(f)
        
        with open(components_file, 'r', encoding='utf-8') as f:
            self.components = json.load(f)
        
        # Crear mapeos ID → índice
        self.profile_id_to_idx = {p['id']: idx for idx, p in enumerate(self.profiles)}
        self.component_id_to_idx = {c['id']: idx for idx, c in enumerate(self.components)}
        
        print(f"\n📊 Dataset cargado:")
        print(f"   Interacciones: {len(self.interactions)}")
        print(f"   Perfiles: {len(self.profiles)}")
        print(f"   Componentes: {len(self.components)}")
    
    def __len__(self):
        return len(self.interactions)
    
    def __getitem__(self, idx):
        interaction = self.interactions[idx]
        
        # Convertir IDs a índices
        profile_idx = self.profile_id_to_idx[interaction['profile_id']]
        component_idx = self.component_id_to_idx[interaction['component_id']]
        rating = interaction['rating']
        
        return {
            'profile_idx': torch.tensor(profile_idx, dtype=torch.long),
            'component_idx': torch.tensor(component_idx, dtype=torch.long),
            'rating': torch.tensor(rating, dtype=torch.float32)
        }

# ==================== ENTRENAMIENTO ====================

def train_epoch(model, dataloader, criterion, optimizer, device):
    """Entrena una época"""
    model.train()
    total_loss = 0
    
    for batch in dataloader:
        profile_ids = batch['profile_idx'].to(device)
        component_ids = batch['component_idx'].to(device)
        ratings = batch['rating'].to(device)
        
        # Forward
        predictions = model(profile_ids, component_ids)
        loss = criterion(predictions, ratings)
        
        # Backward
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    avg_loss = total_loss / len(dataloader)
    return avg_loss

def validate(model, dataloader, criterion, device):
    """Valida el modelo"""
    model.eval()
    total_loss = 0
    
    with torch.no_grad():
        for batch in dataloader:
            profile_ids = batch['profile_idx'].to(device)
            component_ids = batch['component_idx'].to(device)
            ratings = batch['rating'].to(device)
            
            predictions = model(profile_ids, component_ids)
            loss = criterion(predictions, ratings)
            
            total_loss += loss.item()
    
    avg_loss = total_loss / len(dataloader)
    return avg_loss

# ==================== MAIN ====================

def train_ncf_model():
    """Función principal de entrenamiento"""
    
    print("\n" + "="*60)
    print("🧠 ENTRENAMIENTO MODELO NCF")
    print("="*60)
    
    # Paths
    data_dir = Path(__file__).parent.parent / 'data_layer' / 'data'
    interactions_file = data_dir / 'training_interactions.json'
    profiles_file = data_dir / 'training_profiles.json'
    components_file = data_dir / 'components_normalized.json'
    
    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n🖥️  Dispositivo: {device}")
    
    # Dataset
    dataset = ComponentInteractionDataset(
        interactions_file=str(interactions_file),
        profiles_file=str(profiles_file),
        components_file=str(components_file)
    )
    
    # Split train/val (80/20)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        dataset, 
        [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )
    
    print(f"\n📊 Split de datos:")
    print(f"   Train: {len(train_dataset)} interacciones")
    print(f"   Val:   {len(val_dataset)} interacciones")
    
    # DataLoaders
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
    
    # Modelo
    num_profiles = len(dataset.profiles)
    num_components = len(dataset.components)
    
    model = NCFModel(
        num_profiles=num_profiles,
        num_components=num_components,
        embedding_dim=64,
        hidden_layers=[128, 64, 32]
    ).to(device)
    
    print(f"\n🏗️  Modelo NCF creado:")
    print(f"   Perfiles: {num_profiles}")
    print(f"   Componentes: {num_components}")
    print(f"   Parámetros: {sum(p.numel() for p in model.parameters()):,}")
    
    # Loss y optimizer
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Training loop
    num_epochs = 50
    best_val_loss = float('inf')
    patience = 10
    patience_counter = 0
    
    print(f"\n🚀 Iniciando entrenamiento ({num_epochs} épocas)...")
    print("="*60)
    
    for epoch in range(num_epochs):
        train_loss = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss = validate(model, val_loader, criterion, device)
        
        print(f"Época {epoch+1:3d}/{num_epochs} | "
              f"Train Loss: {train_loss:.4f} | "
              f"Val Loss: {val_loss:.4f}")
        
        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            
            # Guardar mejor modelo
            model_path = Path(__file__).parent / 'ncf_model_best.pth'
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
                'profile_id_to_idx': dataset.profile_id_to_idx,
                'component_id_to_idx': dataset.component_id_to_idx
            }, model_path)
            
            print(f"   💾 Mejor modelo guardado (val_loss: {val_loss:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"\n⏸️  Early stopping en época {epoch+1}")
                break
    
    print("\n" + "="*60)
    print("✅ ENTRENAMIENTO COMPLETADO")
    print(f"📊 Mejor Val Loss: {best_val_loss:.4f}")
    print(f"💾 Modelo guardado en: ml_models/ncf_model_best.pth")
    print("="*60 + "\n")

if __name__ == "__main__":
    train_ncf_model()