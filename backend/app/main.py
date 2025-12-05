# backend/app/main.py
"""
API REST del sistema de recomendación de componentes PC
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import sys
from pathlib import Path

# Agregar path del proyecto
sys.path.append(str(Path(__file__).parent.parent))

from api.pc_builder_service import PCBuilderService
from api.chat_parser import ChatParser
from api.recommendation_service import RecommendationService
from config.model_config import get_recommendation_model

# ==================== INICIALIZAR APP ====================

app = FastAPI(
    title="PC Component Recommendation API",
    description="Sistema de recomendación de componentes PC para el mercado peruano",
    version="1.0.0"
)

# CORS (permitir llamadas desde frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servicios globales (se cargan una vez)
pc_builder = None
chat_parser = None
recommender = None

@app.on_event("startup")
async def startup_event():
    """Inicializa servicios al arrancar con los mejores modelos"""
    global pc_builder, chat_parser, recommender
    
    print("\n" + "="*60)
    print("🚀 INICIANDO API REST")
    print("="*60)
    
    # Usar mejores modelos automáticamente (None = usar mejor modelo)
    pc_builder = PCBuilderService(parser_type=None)
    chat_parser = ChatParser()
    recommender = RecommendationService()
    
    # Mostrar qué modelos se están usando
    best_rec_model = get_recommendation_model()
    print(f"✅ Servicios cargados")
    print(f"   🏆 Usando mejor modelo de recomendación: {best_rec_model.upper()}")
    print(f"   🏆 Usando mejor parser conversacional: rule_based")
    print("="*60 + "\n")

# ==================== MODELOS PYDANTIC ====================

class ChatRequest(BaseModel):
    message: str
    
class ChatResponse(BaseModel):
    parsed_data: Dict
    suggested_profile: str

class RecommendationRequest(BaseModel):
    message: str
    model_type: Optional[str] = None  # Si es None, usa automáticamente el mejor modelo
    
class ComponentFilter(BaseModel):
    component_type: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    
class ValidationRequest(BaseModel):
    components: Dict  # {'CPU': {...}, 'GPU': {...}, ...}

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    """Endpoint raíz - información de la API"""
    return {
        "api": "PC Component Recommendation API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/chat",
            "recommend": "/recommend",
            "profiles": "/profiles",
            "components": "/components",
            "validate": "/validate",
            "compare": "/compare-models"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "pc_builder": pc_builder is not None,
            "chat_parser": chat_parser is not None,
            "recommender": recommender is not None
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def parse_chat(request: ChatRequest):
    """
    Parsea mensaje del usuario y extrae requisitos
    
    Ejemplo:
```
    POST /chat
    {
        "message": "Quiero una PC para jugar Valorant, tengo 2000 soles"
    }
```
    """
    try:
        parsed = chat_parser.parse(request.message)
        
        return ChatResponse(
            parsed_data=parsed,
            suggested_profile=parsed['suggested_profile']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend")
async def get_recommendation(request: RecommendationRequest):
    """
    Genera configuración completa de PC basada en mensaje del usuario
    
    Si model_type no se especifica, usa automáticamente el mejor modelo según evaluación.
    
    Ejemplo:
```
    POST /recommend
    {
        "message": "PC para gaming, 2500 soles",
        "model_type": "mf"  # Opcional, si no se especifica usa el mejor modelo
    }
```
    """
    try:
        # Si no se especifica model_type, usar None para que use el mejor modelo
        model_type = request.model_type if request.model_type else None
        
        config = pc_builder.build_pc_configuration(
            user_message=request.message,
            model_type=model_type
        )
        
        return config
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profiles")
async def list_profiles():
    """
    Lista todos los perfiles de usuario disponibles
    
    Retorna:
    - ID del perfil
    - Nombre
    - Rango de presupuesto
    - Componentes prioritarios
    """
    try:
        profiles = recommender.list_profiles()
        return {"profiles": profiles}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profiles/{profile_id}")
async def get_profile_info(profile_id: str):
    """Obtiene información detallada de un perfil"""
    try:
        profile = recommender.get_profile_info(profile_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Perfil no encontrado")
        
        return profile
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/components")
async def list_components(
    component_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 50
):
    """
    Lista componentes con filtros opcionales
    
    Query params:
    - component_type: CPU, GPU, RAM, MOTHERBOARD, STORAGE, PSU, CASE
    - min_price: Precio mínimo
    - max_price: Precio máximo
    - limit: Máximo de resultados (default 50)
    
    Ejemplo:
```
    GET /components?component_type=GPU&max_price=1500
```
    """
    try:
        components = recommender.components
        
        # Filtrar por tipo
        if component_type:
            components = [c for c in components if c['type'] == component_type]
        
        # Filtrar por precio
        if min_price is not None:
            components = [c for c in components if c['regular_price'] >= min_price]
        
        if max_price is not None:
            components = [c for c in components if c['regular_price'] <= max_price]
        
        # Limitar resultados
        components = components[:limit]
        
        return {
            "count": len(components),
            "components": components
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/components/types")
async def get_component_types():
    """Lista los tipos de componentes disponibles"""
    try:
        types = list(set(c['type'] for c in recommender.components))
        
        # Contar componentes por tipo
        type_counts = {}
        for comp_type in types:
            count = len([c for c in recommender.components if c['type'] == comp_type])
            type_counts[comp_type] = count
        
        return {
            "types": sorted(types),
            "counts": type_counts
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validate")
async def validate_configuration(request: ValidationRequest):
    """
    Valida compatibilidad técnica de una configuración
    
    Ejemplo:
```
    POST /validate
    {
        "components": {
            "CPU": {"id": "1234", "features": {...}},
            "MOTHERBOARD": {"id": "5678", "features": {...}},
            ...
        }
    }
```
    """
    try:
        compatibility = pc_builder.validate_compatibility(request.components)
        
        return {
            "is_valid": compatibility['is_valid'],
            "errors": compatibility['errors'],
            "warnings": compatibility['warnings']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare-models")
async def compare_models(request: RecommendationRequest):
    """
    Compara recomendaciones de ambos modelos (NCF vs Reglas)
    
    Ejemplo:
```
    POST /compare-models
    {
        "message": "PC para gaming, 2000 soles"
    }
```
    """
    try:
        comparison = pc_builder.compare_models(request.message)
        
        return comparison
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommend/{profile_id}/{component_type}")
async def recommend_component_by_profile(
    profile_id: str,
    component_type: str,
    model_type: str = 'rule',
    top_k: int = 5
):
    """
    Recomienda componentes específicos para un perfil
    
    Ejemplo:
```
    GET /recommend/gamer_mid/GPU?model_type=rule&top_k=5
```
    """
    try:
        recommendations = recommender.recommend(
            profile_id=profile_id,
            model_type=model_type,
            top_k=top_k,
            component_type=component_type
        )
        
        return {
            "profile_id": profile_id,
            "component_type": component_type,
            "model_used": model_type,
            "recommendations": recommendations
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 INICIANDO SERVIDOR FASTAPI")
    print("="*60)
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )