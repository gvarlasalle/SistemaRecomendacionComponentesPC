# Guía de Modelos y Evaluación

Este documento explica cómo usar y evaluar los diferentes modelos implementados en el sistema.

## Modelos de Filtrado Colaborativo

El sistema incluye 4 modelos diferentes para recomendación de componentes:

### 1. Rule-Based (Basado en Reglas)
- **Archivo**: `ml_models/rule_based_recommender.py`
- **Tipo**: Basado en reglas y scoring de features
- **Ventajas**: Rápido, interpretable, no requiere entrenamiento
- **Uso**: `model_type='rule'`

### 2. NCF (Neural Collaborative Filtering)
- **Archivo**: `ml_models/ncf_model.py`
- **Tipo**: Red neuronal con embeddings y MLP
- **Ventajas**: Captura interacciones no lineales
- **Entrenamiento**: `python ml_models/train_ncf.py`
- **Uso**: `model_type='ncf'`

### 3. MF (Matrix Factorization)
- **Archivo**: `ml_models/mf_model.py`
- **Tipo**: Factorización matricial tradicional
- **Ventajas**: Simple, eficiente, bueno para datos escasos
- **Entrenamiento**: `python ml_models/train_mf.py`
- **Uso**: `model_type='mf'`

### 4. DeepFM (Deep Factorization Machine)
- **Archivo**: `ml_models/deepfm_model.py`
- **Tipo**: Combina factorización y redes profundas
- **Ventajas**: Mejor de ambos mundos (FM + Deep)
- **Entrenamiento**: `python ml_models/train_deepfm.py`
- **Uso**: `model_type='deepfm'`

## Modelos Conversacionales

El sistema incluye 3 parsers diferentes para entender mensajes del usuario:

### 1. Rule-Based Parser
- **Archivo**: `api/chat_parser.py`
- **Tipo**: Regex y keywords
- **Ventajas**: Rápido, simple, no requiere dependencias externas
- **Uso**: `parser_type='rule'` (default)

### 2. spaCy Parser
- **Archivo**: `api/chat_parser_spacy.py`
- **Tipo**: Usa spaCy NER (reconocimiento de entidades nombradas)
- **Ventajas**: Mejor extracción de entidades, más robusto
- **Requisitos**: Modelo spaCy instalado (`python -m spacy download es_core_news_sm`)
- **Uso**: `parser_type='spacy'`

### 3. Embedding Parser
- **Archivo**: `api/chat_parser_embedding.py`
- **Tipo**: TF-IDF y similitud semántica
- **Ventajas**: Mejor comprensión de contexto y similitud
- **Uso**: `parser_type='embedding'`

## Evaluación de Modelos

### Evaluar Modelos de Recomendación

```bash
python ml_models/model_evaluator.py
```

Métricas calculadas:
- **RMSE** (Root Mean Squared Error): Error cuadrático medio
- **MAE** (Mean Absolute Error): Error absoluto medio
- **Precision@K**: Precisión en top-K recomendaciones
- **Recall@K**: Recuperación en top-K recomendaciones
- **NDCG@K**: Normalized Discounted Cumulative Gain

### Evaluar Modelos Conversacionales

```bash
python api/conversational_evaluator.py
```

Métricas calculadas:
- **Budget Accuracy**: Precisión en extracción de presupuesto
- **Use Case Accuracy**: Precisión en detección de casos de uso
- **Profile Accuracy**: Precisión en mapeo a perfiles
- **Overall Accuracy**: Precisión general (promedio)

### Evaluación Completa

Para evaluar todos los modelos y obtener recomendaciones:

```bash
python evaluate_all_models.py
```

Este script:
1. Evalúa todos los modelos de recomendación
2. Evalúa todos los modelos conversacionales
3. Determina el mejor modelo de cada tipo
4. Guarda resultados en `ml_models/complete_evaluation_results.json`

## Entrenamiento de Modelos

### Entrenar NCF
```bash
python ml_models/train_ncf.py
```

### Entrenar Matrix Factorization
```bash
python ml_models/train_mf.py
```

### Entrenar DeepFM
```bash
python ml_models/train_deepfm.py
```

**Nota**: Los modelos se guardan automáticamente en `ml_models/` con el formato `{model_name}_model_best.pth`

## Uso en Producción

### Ejemplo básico

```python
from api.pc_builder_service import PCBuilderService

# Usar mejores modelos (determinados por evaluación)
service = PCBuilderService(parser_type='rule')  # o 'spacy', 'embedding'
config = service.build_pc_configuration(
    "Quiero una PC para jugar Valorant, tengo 2000 soles",
    model_type='rule'  # o 'ncf', 'mf', 'deepfm'
)
```

### Comparar modelos

```python
from api.pc_builder_service import PCBuilderService

service = PCBuilderService()

# Comparar recomendaciones de diferentes modelos
comparison = service.compare_models("Quiero una PC para gaming, 2000 soles")
print(comparison['ncf'])
print(comparison['rules'])
```

## Mejoras Implementadas

### Compatibilidad Mejorada
- Validación exhaustiva de socket CPU/Motherboard
- Verificación de tipo de RAM compatible
- Validación de longitud de GPU vs Case
- Verificación de slots M.2 disponibles
- Validación de wattage de PSU vs consumo total

### Control de Presupuesto Mejorado
- Límite máximo de 5% de exceso (antes 10-20%)
- Ajuste iterativo post-selección
- Priorización de componentes dentro del presupuesto asignado
- Optimización inteligente que busca alternativas más económicas

## Métricas de Evaluación

### Para Modelos de Recomendación

**RMSE y MAE**: Miden qué tan bien predice el modelo los ratings reales.
- Menor es mejor
- RMSE penaliza más los errores grandes

**Precision@K y Recall@K**: Miden la calidad de las recomendaciones.
- Precision@K: De los K recomendados, ¿cuántos son relevantes?
- Recall@K: De los relevantes, ¿cuántos están en los K recomendados?

**NDCG@K**: Mide la calidad del ranking considerando la posición.
- Mayor es mejor (rango 0-1)
- Considera que los primeros resultados son más importantes

### Para Modelos Conversacionales

**Budget Accuracy**: ¿Qué tan bien extrae el presupuesto?
- Compara presupuesto extraído vs esperado

**Use Case Accuracy**: ¿Qué tan bien detecta los casos de uso?
- Verifica si detecta al menos un caso de uso correcto

**Profile Accuracy**: ¿Qué tan bien mapea a perfiles?
- Compara perfil sugerido vs esperado

## Selección del Mejor Modelo

El sistema selecciona automáticamente el mejor modelo basándose en:

**Modelos de Recomendación**:
- Score combinado: 40% RMSE normalizado + 60% NDCG@10
- El modelo con mayor score combinado gana

**Modelos Conversacionales**:
- Overall Accuracy (promedio de todas las métricas)
- El parser con mayor overall accuracy gana

## Resultados

Los resultados de evaluación se guardan en:
- `ml_models/model_comparison_results.json` - Comparación de modelos de recomendación
- `ml_models/conversational_comparison_results.json` - Comparación de parsers
- `ml_models/complete_evaluation_results.json` - Resultados completos

