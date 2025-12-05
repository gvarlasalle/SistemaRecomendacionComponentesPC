# backend/ml_models/train_mf.py
"""
Entrena el modelo Matrix Factorization (MF)
"""

import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from ml_models.mf_model import MFModel
from ml_models.train_ncf import ComponentInteractionDataset

def train_mf_model():
    """Función principal de entrenamiento"""
    
    print("\n" + "="*60)
    print("🧠 ENTRENAMIENTO MODELO MATRIX FACTORIZATION")
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
    
    model = MFModel(
        num_profiles=num_profiles,
        num_components=num_components,
        embedding_dim=64
    ).to(device)
    
    print(f"\n🏗️  Modelo MF creado:")
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
        # Train
        model.train()
        train_loss = 0
        for batch in train_loader:
            profile_ids = batch['profile_idx'].to(device)
            component_ids = batch['component_idx'].to(device)
            ratings = batch['rating'].to(device)
            
            predictions = model(profile_ids, component_ids)
            loss = criterion(predictions, ratings)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        train_loss /= len(train_loader)
        
        # Validate
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for batch in val_loader:
                profile_ids = batch['profile_idx'].to(device)
                component_ids = batch['component_idx'].to(device)
                ratings = batch['rating'].to(device)
                
                predictions = model(profile_ids, component_ids)
                loss = criterion(predictions, ratings)
                val_loss += loss.item()
        
        val_loss /= len(val_loader)
        
        print(f"Época {epoch+1:3d}/{num_epochs} | "
              f"Train Loss: {train_loss:.4f} | "
              f"Val Loss: {val_loss:.4f}")
        
        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            
            # Guardar mejor modelo
            model_path = Path(__file__).parent / 'mf_model_best.pth'
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
    print(f"💾 Modelo guardado en: ml_models/mf_model_best.pth")
    print("="*60 + "\n")

if __name__ == "__main__":
    train_mf_model()

