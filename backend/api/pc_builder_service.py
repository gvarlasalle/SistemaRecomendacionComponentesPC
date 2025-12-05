# backend/api/pc_builder_service.py
"""
Servicio principal con optimización de presupuesto y compatibilidad
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional

sys.path.append(str(Path(__file__).parent.parent))

from api.chat_parser import ChatParser
from api.recommendation_service import RecommendationService

# Imports condicionales para parsers alternativos
try:
    from api.chat_parser_spacy import ChatParserSpacy
except ImportError:
    ChatParserSpacy = None

try:
    from api.chat_parser_embedding import ChatParserEmbedding
except ImportError:
    ChatParserEmbedding = None

# Importar configuración de mejores modelos
try:
    from config.model_config import get_conversational_model, get_recommendation_model
except ImportError:
    # Fallback si no se puede importar
    def get_conversational_model():
        return 'rule'
    def get_recommendation_model():
        return 'mf'

class PCBuilderService:
    """Servicio principal con optimización inteligente"""
    
    def __init__(self, parser_type: Optional[str] = None):
        """
        Inicializa el servicio con los mejores modelos por defecto
        
        Args:
            parser_type: 'rule', 'spacy', o 'embedding'. Si es None, usa el mejor modelo automáticamente
        """
        # Usar mejor modelo conversacional si no se especifica
        if parser_type is None:
            parser_type = get_conversational_model()
        
        if parser_type == 'spacy':
            if ChatParserSpacy is None:
                print("⚠️  spaCy no está disponible, usando parser basado en reglas")
                self.chat_parser = ChatParser()
            else:
                self.chat_parser = ChatParserSpacy()
        elif parser_type == 'embedding':
            if ChatParserEmbedding is None:
                print("⚠️  Embedding parser no está disponible, usando parser basado en reglas")
                self.chat_parser = ChatParser()
            else:
                self.chat_parser = ChatParserEmbedding()
        else:
            self.chat_parser = ChatParser()
        
        self.recommender = RecommendationService()
        self.default_model_type = get_recommendation_model()
        
        print("\n✅ PC Builder Service inicializado")
        print(f"   Parser: {parser_type}")
        print(f"   Modelo de recomendación por defecto: {self.default_model_type}")
    
    def filter_compatible_components(self, candidates: List[Dict], 
                                     selected_components: Dict,
                                     component_type: str) -> List[Dict]:
        """
        Filtra componentes compatibles con los ya seleccionados
        Versión mejorada con más validaciones
        """
        if not candidates:
            return []
        
        compatible = []
        
        for candidate in candidates:
            is_compatible = True
            features = candidate.get('features', {})
            
            # === CPU ↔ Motherboard === (VALIDACIÓN ESTRICTA)
            if component_type == 'CPU' and 'MOTHERBOARD' in selected_components:
                cpu_socket = features.get('socket', '').upper().strip()
                mb_socket = selected_components['MOTHERBOARD'].get('features', {}).get('socket', '').upper().strip()
                # Validación estricta: ambos deben tener socket y deben coincidir
                if cpu_socket and mb_socket:
                    if cpu_socket != mb_socket:
                        is_compatible = False
                        continue
                # Si falta información de socket, no podemos validar - rechazar por seguridad
                elif cpu_socket and not mb_socket:
                    # CPU tiene socket pero motherboard no especifica - rechazar por seguridad
                    is_compatible = False
                    continue
                elif not cpu_socket and mb_socket:
                    # Motherboard tiene socket pero CPU no especifica - rechazar por seguridad
                    is_compatible = False
                    continue
            
            elif component_type == 'MOTHERBOARD' and 'CPU' in selected_components:
                mb_socket = features.get('socket', '').upper().strip()
                cpu_socket = selected_components['CPU'].get('features', {}).get('socket', '').upper().strip()
                # Validación estricta: ambos deben tener socket y deben coincidir
                if mb_socket and cpu_socket:
                    if mb_socket != cpu_socket:
                        is_compatible = False
                        continue
                # Si falta información de socket, rechazar por seguridad
                elif mb_socket and not cpu_socket:
                    is_compatible = False
                    continue
                elif not mb_socket and cpu_socket:
                    is_compatible = False
                    continue
            
            # === RAM ↔ Motherboard ===
            if component_type == 'RAM' and 'MOTHERBOARD' in selected_components:
                ram_type = str(features.get('ram_type', '')).upper().strip()
                mb_ram_type = str(selected_components['MOTHERBOARD'].get('features', {}).get('supported_ram_type', '')).upper().strip()
                
                # Validación estricta: si ambos tienen tipo definido, deben coincidir
                if ram_type and mb_ram_type:
                    if ram_type != mb_ram_type:
                        is_compatible = False
                        continue
                # Si la RAM no tiene tipo definido, rechazar por seguridad
                elif not ram_type and mb_ram_type:
                    is_compatible = False
                    continue
                # Si la motherboard no especifica tipo, permitir (pero será validado después)
                elif ram_type and not mb_ram_type:
                    # Permitir pero será validado después
                    pass
                # Si ninguno tiene tipo, rechazar por seguridad
                elif not ram_type and not mb_ram_type:
                    is_compatible = False
                    continue
                
                # Verificar slots disponibles (solo si se especifica)
                ram_slots = selected_components['MOTHERBOARD'].get('features', {}).get('ram_slots', 0)
                if ram_slots > 0:  # Solo validar si se especifica
                    # Contar RAM seleccionadas (incluyendo RAM_2, RAM_3, etc.)
                    ram_count = sum(1 for k in selected_components.keys() if k.startswith('RAM'))
                    if ram_count >= ram_slots:
                        is_compatible = False
                        continue
            
            elif component_type == 'MOTHERBOARD' and 'RAM' in selected_components:
                mb_ram_type = features.get('supported_ram_type', '').upper()
                ram_type = selected_components['RAM'].get('features', {}).get('ram_type', '').upper()
                if mb_ram_type and ram_type and mb_ram_type != ram_type:
                    is_compatible = False
                    continue
            
            # === GPU ↔ Case (form factor) ===
            if component_type == 'GPU' and 'CASE' in selected_components:
                gpu_length = features.get('length_mm', 0)
                case_max_length = selected_components['CASE'].get('features', {}).get('max_gpu_length_mm', 9999)
                if gpu_length > case_max_length:
                    is_compatible = False
                    continue
            
            # === Storage ↔ Motherboard (M.2 slots) ===
            if component_type == 'STORAGE' and 'MOTHERBOARD' in selected_components:
                storage_type = features.get('storage_type', '').upper()
                if storage_type == 'M.2' or storage_type == 'NVME':
                    m2_slots = selected_components['MOTHERBOARD'].get('features', {}).get('m2_slots', 0)
                    m2_count = sum(1 for k, v in selected_components.items() 
                                 if k == 'STORAGE' and v.get('features', {}).get('storage_type', '').upper() in ['M.2', 'NVME'])
                    if m2_count >= m2_slots:
                        is_compatible = False
                        continue
            
            # === PSU ↔ Components (wattage) ===
            if component_type == 'PSU':
                # Verificar si hay componentes que requieren mucha potencia
                total_power = 0
                if 'CPU' in selected_components:
                    total_power += selected_components['CPU'].get('features', {}).get('tdp_watts', 65)
                if 'GPU' in selected_components:
                    total_power += selected_components['GPU'].get('features', {}).get('tdp_watts', 150)
                total_power += 50  # Overhead
                
                psu_wattage = features.get('wattage', 0)
                if psu_wattage < total_power * 1.1:  # 10% de margen mínimo
                    is_compatible = False
                    continue
            
            if is_compatible:
                compatible.append(candidate)
        
        return compatible
    
    def _try_fix_compatibility(self, target_type: str, selected_components: Dict,
                                profile_id: str, model_type: str, budget: float) -> List[Dict]:
        """
        Intenta arreglar problemas de compatibilidad ajustando componentes ya seleccionados
        """
        # Si el problema es con CPU/Motherboard, intentar cambiar el que no es target_type
        if target_type in ['CPU', 'MOTHERBOARD']:
            other_type = 'MOTHERBOARD' if target_type == 'CPU' else 'CPU'
            if other_type in selected_components:
                # Obtener candidatos para el otro componente que sean compatibles
                candidates_other = self.recommender.recommend(
                    profile_id=profile_id,
                    model_type=model_type,
                    top_k=50,
                    component_type=other_type
                )
                
                # Crear componentes temporales sin el componente problemático
                temp_components = {k: v for k, v in selected_components.items() if k != other_type}
                
                # Buscar un componente compatible para el otro tipo
                for candidate in candidates_other:
                    temp_components[other_type] = candidate
                    compatible = self.filter_compatible_components(
                        [candidate], temp_components, other_type
                    )
                    if compatible:
                        # Si encontramos uno compatible, ahora intentar el target_type
                        candidates_target = self.recommender.recommend(
                            profile_id=profile_id,
                            model_type=model_type,
                            top_k=50,
                            component_type=target_type
                        )
                        compatible_target = self.filter_compatible_components(
                            candidates_target, temp_components, target_type
                        )
                        if compatible_target:
                            # Actualizar el componente en selected_components
                            selected_components[other_type] = candidate
                            return compatible_target
        
        # Si el problema es con RAM/Motherboard
        elif target_type in ['RAM', 'MOTHERBOARD']:
            other_type = 'MOTHERBOARD' if target_type == 'RAM' else 'RAM'
            if other_type in selected_components:
                candidates_other = self.recommender.recommend(
                    profile_id=profile_id,
                    model_type=model_type,
                    top_k=50,
                    component_type=other_type
                )
                
                temp_components = {k: v for k, v in selected_components.items() if k != other_type}
                
                for candidate in candidates_other:
                    temp_components[other_type] = candidate
                    compatible = self.filter_compatible_components(
                        [candidate], temp_components, other_type
                    )
                    if compatible:
                        candidates_target = self.recommender.recommend(
                            profile_id=profile_id,
                            model_type=model_type,
                            top_k=50,
                            component_type=target_type
                        )
                        compatible_target = self.filter_compatible_components(
                            candidates_target, temp_components, target_type
                        )
                        if compatible_target:
                            selected_components[other_type] = candidate
                            return compatible_target
        
        return []
    
    def validate_compatibility(self, components: Dict) -> Dict:
        """Valida compatibilidad técnica"""
        errors = []
        warnings = []
        
        cpu = components.get('CPU')
        motherboard = components.get('MOTHERBOARD')
        ram = components.get('RAM')
        psu = components.get('PSU')
        gpu = components.get('GPU')
        
        # CPU ↔ Motherboard
        if cpu and motherboard:
            cpu_socket = cpu.get('features', {}).get('socket', '')
            mb_socket = motherboard.get('features', {}).get('socket', '')
            if cpu_socket and mb_socket and cpu_socket != mb_socket:
                errors.append(f"CPU {cpu_socket} ≠ Motherboard {mb_socket}")
        
        # RAM ↔ Motherboard
        if ram and motherboard:
            ram_type = ram.get('features', {}).get('ram_type', '')
            mb_ram_type = motherboard.get('features', {}).get('supported_ram_type', '')
            if ram_type and mb_ram_type and ram_type != mb_ram_type:
                errors.append(f"RAM {ram_type} ≠ Motherboard {mb_ram_type}")
        
        # PSU
        if psu:
            psu_wattage = psu.get('features', {}).get('wattage', 0)
            total_consumption = 0
            if cpu:
                total_consumption += cpu.get('features', {}).get('tdp_watts', 65)
            if gpu:
                total_consumption += gpu.get('features', {}).get('tdp_watts', 150)
            total_consumption += 50
            
            recommended_psu = total_consumption * 1.3
            
            if psu_wattage < total_consumption:
                errors.append(f"PSU {psu_wattage}W < {total_consumption}W necesarios")
            elif psu_wattage < recommended_psu:
                warnings.append(f"PSU {psu_wattage}W. Recomendado: {int(recommended_psu)}W")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def build_pc_configuration(self, user_message: str, model_type: Optional[str] = None) -> Dict:
        """
        Construye configuración con límites estrictos de presupuesto
        
        Args:
            user_message: Mensaje del usuario
            model_type: Tipo de modelo ('rule', 'ncf', 'mf', 'deepfm'). 
                       Si es None, usa el mejor modelo automáticamente
        """
        # Usar mejor modelo si no se especifica
        if model_type is None:
            model_type = self.default_model_type
        
        # 1. Parsear mensaje
        parsed = self.chat_parser.parse(user_message)
        
        print(f"\n{'='*60}")
        print(f"💬 Mensaje: {user_message}")
        print(f"{'='*60}")
        print(f"📊 Detectado:")
        print(f"   Presupuesto: S/ {parsed['budget']}")
        print(f"   Perfil: {parsed['suggested_profile']}")
        print(f"   Prioridades: {' > '.join(parsed['priorities'])}")
        
        # 2. Distribución de presupuesto según perfil
        profile_id = parsed['suggested_profile']
        budget = parsed['budget']
        use_cases = parsed['use_cases']
        
        # Distribución porcentual según caso de uso Y presupuesto
        # Para presupuestos bajos (< 1200), optimizar más agresivamente
        is_low_budget = budget < 1200
        
        if 'gaming' in use_cases:
            if is_low_budget:
                # Gaming con presupuesto ajustado: priorizar GPU y CPU para máximo rendimiento
                budget_distribution = {
                    'GPU': 0.38,      # Prioridad máxima para gaming
                    'CPU': 0.25,      # Mantener CPU potente
                    'MOTHERBOARD': 0.10,  # Reducido
                    'RAM': 0.12,      # Suficiente para gaming
                    'STORAGE': 0.10,  # Básico
                    'PSU': 0.04,      # Mínimo necesario
                    'CASE': 0.01      # Mínimo
                }
            else:
                # Gaming normal: maximizar GPU y CPU para mejor rendimiento
                budget_distribution = {
                    'GPU': 0.42,      # Aumentado para mejor GPU
                    'CPU': 0.28,      # Aumentado para mejor CPU
                    'MOTHERBOARD': 0.10,  # Reducido
                    'RAM': 0.10,      # Suficiente
                    'STORAGE': 0.06,  # Reducido
                    'PSU': 0.03,      # Mínimo
                    'CASE': 0.01      # Mínimo
                }
            required_components = ['CPU', 'GPU', 'RAM', 'MOTHERBOARD', 'STORAGE', 'PSU', 'CASE']
        elif 'development' in use_cases:
            if is_low_budget:
                # Desarrollo con presupuesto ajustado: priorizar CPU y RAM
                budget_distribution = {
                    'CPU': 0.35,      # Prioridad máxima para desarrollo
                    'RAM': 0.25,      # Alto para desarrollo
                    'STORAGE': 0.15,  # Suficiente
                    'MOTHERBOARD': 0.12,  # Básico
                    'PSU': 0.10,      # Adecuado
                    'CASE': 0.03      # Mínimo
                }
            else:
                # Desarrollo normal: maximizar CPU y RAM para mejor rendimiento
                budget_distribution = {
                    'CPU': 0.40,      # Aumentado para mejor CPU
                    'RAM': 0.25,      # Aumentado para más RAM
                    'STORAGE': 0.15,  # Suficiente
                    'MOTHERBOARD': 0.12,  # Básico
                    'PSU': 0.06,      # Adecuado
                    'CASE': 0.02      # Mínimo
                }
            required_components = ['CPU', 'RAM', 'MOTHERBOARD', 'STORAGE', 'PSU', 'CASE']  # GPU opcional
        elif 'design' in use_cases or 'video_editing' in use_cases:
            # Para diseño/edición: priorizar GPU, CPU y RAM
            # Si también hay gaming, aumentar GPU aún más
            has_gaming = 'gaming' in use_cases
            is_high_budget = budget > 3000  # Presupuesto alto
            
            if is_low_budget:
                budget_distribution = {
                    'GPU': 0.35 if has_gaming else 0.30,
                    'CPU': 0.25,
                    'RAM': 0.20,      # Aumentado para edición
                    'MOTHERBOARD': 0.10,
                    'STORAGE': 0.08,
                    'PSU': 0.02,
                    'CASE': 0.00
                }
            elif is_high_budget:
                # Para presupuestos altos: maximizar GPU, CPU y RAM
                # Asegurar que se use más del presupuesto (85-95%)
                budget_distribution = {
                    'GPU': 0.42 if has_gaming else 0.38,  # Aumentado para gaming + edición
                    'CPU': 0.38,      # Aumentado aún más para edición y streaming (de 35% a 38%)
                    'RAM': 0.25,      # Aumentado para edición de video (idealmente 32GB+) (de 22% a 25%)
                    'MOTHERBOARD': 0.00,  # Mínimo necesario
                    'STORAGE': 0.00,  # Mínimo (pero debería ser NVMe)
                    'PSU': 0.00,      # Mínimo necesario
                    'CASE': 0.00      # Mínimo
                }
            else:
                # Presupuesto normal
                budget_distribution = {
                    'GPU': 0.40 if has_gaming else 0.35,
                    'CPU': 0.30,
                    'RAM': 0.18,
                    'MOTHERBOARD': 0.08,
                    'STORAGE': 0.04,
                    'PSU': 0.00,
                    'CASE': 0.00
                }
            required_components = ['CPU', 'GPU', 'RAM', 'MOTHERBOARD', 'STORAGE', 'PSU', 'CASE']
        else:  # office/student
            if is_low_budget:
                # Para oficina con presupuesto bajo: optimizar motherboard y case
                budget_distribution = {
                    'CPU': 0.35,      # Reducido de 40% para optimizar
                    'RAM': 0.20,      # Reducido ligeramente
                    'MOTHERBOARD': 0.12,  # Reducido significativamente de 18%
                    'STORAGE': 0.15,  # Aumentado
                    'PSU': 0.10,      # Aumentado para mejor calidad
                    'CASE': 0.08      # Aumentado de 2% para opciones básicas funcionales
                }
            else:
                budget_distribution = {
                    'CPU': 0.40,
                    'RAM': 0.22,
                    'MOTHERBOARD': 0.18,
                    'STORAGE': 0.12,
                    'PSU': 0.06,
                    'CASE': 0.02
                }
            required_components = ['CPU', 'RAM', 'MOTHERBOARD', 'STORAGE', 'PSU', 'CASE']  # Sin GPU
        
        # 3. Orden de selección (optimizado para compatibilidad)
        # Orden crítico: Motherboard primero (define compatibilidades), luego CPU, RAM, etc.
        priorities = parsed['priorities']
        all_types = list(budget_distribution.keys())
        
        # Orden inteligente: componentes que definen compatibilidad primero
        compatibility_order = ['MOTHERBOARD', 'CPU', 'RAM']  # Estos definen las compatibilidades principales
        
        ordered_types = []
        
        # 1. Agregar componentes críticos para compatibilidad primero
        for comp_type in compatibility_order:
            if comp_type in all_types:
                ordered_types.append(comp_type)
        
        # 2. Agregar prioridades del usuario (si no están ya)
        for priority in priorities:
            if priority in all_types and priority not in ordered_types:
                ordered_types.append(priority)
        
        # 3. Agregar el resto
        for comp_type in all_types:
            if comp_type not in ordered_types:
                ordered_types.append(comp_type)
        
        # 4. Selección con límites estrictos
        components = {}
        total_cost = 0
        skipped_components = []
        
        print(f"\n🔍 Recomendando componentes (modelo: {model_type})...")
        print(f"💰 Distribución de presupuesto:")
        
        for comp_type in ordered_types:
            allocated_budget = budget * budget_distribution.get(comp_type, 0.10)
            required = "✓" if comp_type in required_components else "○"
            print(f"   {required} {comp_type:12s}: max S/ {allocated_budget:.0f} ({budget_distribution.get(comp_type, 0.10)*100:.0f}%)")
        
        print(f"\n🛠️  Seleccionando componentes...")
        
        # Presupuesto restante disponible
        remaining_budget = budget
        
        # Detectar gaming 4K o alto rendimiento desde el mensaje (una sola vez antes del loop)
        is_gaming_4k = 'gaming' in use_cases and any(x in user_message.lower() for x in ['4k', '4 k', 'alto rendimiento', 'aaa', 'triple a'])
        
        for comp_type in ordered_types:
            allocated_budget = budget * budget_distribution.get(comp_type, 0.10)
            
            # Para presupuestos bajos, ser más estricto
            # Para presupuestos altos, permitir más flexibilidad para componentes de gama alta
            is_high_budget = budget > 3000
            
            if is_low_budget:
                # Máximo 5% de exceso sobre lo asignado para presupuestos bajos
                max_price = allocated_budget * 1.05
            elif is_high_budget:
                # Para presupuestos altos, permitir hasta 20% de exceso para componentes críticos
                # Esto permite seleccionar componentes de gama alta
                is_critical = comp_type in ['CPU', 'GPU', 'RAM']
                max_price = allocated_budget * 1.20 if is_critical else allocated_budget * 1.15
            else:
                # Máximo 10% de exceso para presupuestos normales
                max_price = allocated_budget * 1.1
            
            # Pero también considerar presupuesto restante real
            # Para presupuestos bajos, ser más conservador
            # Para presupuestos altos, ser más flexible
            if is_low_budget:
                remaining_multiplier = 1.02
            elif is_high_budget:
                remaining_multiplier = 1.10  # Más flexible para usar el presupuesto
            else:
                remaining_multiplier = 1.05
            max_price = min(max_price, remaining_budget * remaining_multiplier)
            
            # ESTRATEGIA MEJORADA: Obtener TODOS los componentes del tipo y filtrar por compatibilidad primero
            # Esto asegura encontrar componentes compatibles aunque tengan rating más bajo
            # Usar un número muy grande para obtener todos los componentes del tipo
            all_candidates = self.recommender.recommend(
                profile_id=profile_id,
                model_type=model_type,
                top_k=1000,  # Número muy grande para obtener TODOS los componentes del tipo
                component_type=comp_type
            )
            
            # Filtrar por compatibilidad PRIMERO (OBLIGATORIO - nunca usar incompatibles)
            compatible_candidates = self.filter_compatible_components(
                all_candidates, 
                components, 
                comp_type
            )
            
            # Si hay compatibles, mantener el orden por rating (ya viene ordenado del recommend)
            # Si no hay compatibles, intentar ajustar componentes existentes
            if not compatible_candidates:
                print(f"   ⚠️  {comp_type:12s}: No hay componentes compatibles en {len(all_candidates)} candidatos")
                
                # Si es componente requerido, intentar ajustar componentes existentes
                if comp_type in required_components:
                    print(f"   🔄 {comp_type:12s}: Intentando ajustar componentes existentes para encontrar compatibles...")
                    compatible_candidates = self._try_fix_compatibility(
                        comp_type, components, profile_id, model_type, budget
                    )
                
                if not compatible_candidates:
                    print(f"   ❌ {comp_type:12s}: No se encontraron componentes compatibles después de ajustes")
                    print(f"   ⊗ {comp_type:12s}: Omitido (sin componentes compatibles)")
                    skipped_components.append(comp_type)
                    continue
            else:
                # Si encontramos compatibles, mostrar cuántos
                if len(compatible_candidates) < len(all_candidates):
                    print(f"   ℹ️  {comp_type:12s}: {len(compatible_candidates)} compatibles de {len(all_candidates)} candidatos")
            
            # Filtrar por precio: primero intentar dentro del presupuesto asignado
            affordable_candidates = [c for c in compatible_candidates if c['price'] <= allocated_budget]
            
            # Si no hay dentro del presupuesto asignado, buscar dentro del límite máximo
            # Pero para presupuestos bajos, ser más estricto
            if not affordable_candidates:
                if is_low_budget:
                    # Para presupuestos bajos, buscar solo hasta 3% de exceso sobre lo asignado
                    strict_max = allocated_budget * 1.03
                    affordable_candidates = [c for c in compatible_candidates if c['price'] <= strict_max]
                    # Si aún no hay, buscar hasta el límite máximo pero priorizar los más baratos
                    if not affordable_candidates:
                        affordable_candidates = [c for c in compatible_candidates if c['price'] <= max_price]
                        # Ordenar por precio (más barato primero) para presupuestos bajos
                        affordable_candidates.sort(key=lambda x: x['price'])
                else:
                    affordable_candidates = [c for c in compatible_candidates if c['price'] <= max_price]
            
            selected = None
            
            # Selección inteligente - SOLO de componentes compatibles
            # ESTRATEGIA: Maximizar rendimiento según caso de uso y presupuesto
            if affordable_candidates:
                # Determinar qué componentes son críticos para el rendimiento según el caso de uso
                is_performance_critical = False
                if 'gaming' in use_cases and comp_type in ['CPU', 'GPU']:
                    is_performance_critical = True
                elif 'development' in use_cases and comp_type in ['CPU', 'RAM']:
                    is_performance_critical = True
                elif 'design' in use_cases or 'video_editing' in use_cases:
                    is_performance_critical = comp_type in ['CPU', 'GPU', 'RAM', 'STORAGE']
                elif comp_type == 'CPU':  # CPU siempre es importante para rendimiento
                    is_performance_critical = True
                
                if is_performance_critical:
                    # Para componentes críticos: MAXIMIZAR RENDIMIENTO (rating)
                    # Para presupuestos altos, buscar componentes de gama alta
                    is_high_budget = budget > 3000
                    
                    # Filtrar gama baja para gaming o presupuestos altos
                    if ('gaming' in use_cases and comp_type in ['CPU', 'GPU']) or (is_high_budget and comp_type in ['CPU', 'GPU']):
                        # Para presupuestos altos O gaming 4K, priorizar gama alta (i7/i9, Ryzen 7/9)
                        is_high_performance_needed = is_high_budget or is_gaming_4k
                        if is_high_performance_needed and comp_type == 'CPU':
                            high_end_candidates = []
                            for c in affordable_candidates:
                                name = c['name'].upper()
                                is_high_end = any(x in name for x in ['RYZEN 7', 'RYZEN 9', 'CORE I7', 'CORE I9'])
                                if is_high_end:
                                    high_end_candidates.append(c)
                            
                            if high_end_candidates:
                                # Para presupuestos altos, elegir el mejor rating entre gama alta
                                best_rating = max(c['predicted_rating'] for c in high_end_candidates)
                                top_rated = [c for c in high_end_candidates 
                                           if c['predicted_rating'] >= best_rating * 0.98]
                                # Elegir el más caro (mejor gama) entre los mejor calificados
                                selected = max(top_rated, key=lambda x: x['price'])
                            else:
                                # Si no hay gama alta, usar lógica normal
                                mid_range_candidates = []
                                for c in affordable_candidates:
                                    name = c['name'].upper()
                                    is_low_end = any(x in name for x in ['RYZEN 3', 'CORE I3', 'ATHLON', 'PENTIUM', 'CELERON'])
                                    is_mid_high = any(x in name for x in ['RYZEN 5', 'RYZEN 7', 'RYZEN 9', 
                                                                           'CORE I5', 'CORE I7', 'CORE I9'])
                                    if is_mid_high or (not is_low_end and c['predicted_rating'] >= 3.0):
                                        mid_range_candidates.append(c)
                                
                                if mid_range_candidates:
                                    best_rating = max(c['predicted_rating'] for c in mid_range_candidates)
                                    top_rated = [c for c in mid_range_candidates 
                                               if c['predicted_rating'] >= best_rating * 0.95]
                                    selected = max(top_rated, key=lambda x: x['price'])
                                else:
                                    best_rating = max(c['predicted_rating'] for c in affordable_candidates)
                                    top_rated = [c for c in affordable_candidates 
                                               if c['predicted_rating'] >= best_rating * 0.95]
                                    selected = max(top_rated, key=lambda x: x['price'])
                        else:
                            # Para GPU o gaming normal
                            mid_range_candidates = []
                            for c in affordable_candidates:
                                name = c['name'].upper()
                                is_low_end = any(x in name for x in ['RYZEN 3', 'CORE I3', 'ATHLON', 'PENTIUM', 'CELERON'])
                                is_mid_high = any(x in name for x in ['RYZEN 5', 'RYZEN 7', 'RYZEN 9', 
                                                                       'CORE I5', 'CORE I7', 'CORE I9'])
                                if is_mid_high or (not is_low_end and c['predicted_rating'] >= 3.0):
                                    mid_range_candidates.append(c)
                            
                            if mid_range_candidates:
                                # Elegir el MEJOR rating (máximo rendimiento)
                                best_rating = max(c['predicted_rating'] for c in mid_range_candidates)
                                # Para presupuestos altos, ser más estricto (solo top 2%)
                                tolerance = 0.98 if is_high_budget else 0.95
                                top_rated = [c for c in mid_range_candidates 
                                           if c['predicted_rating'] >= best_rating * tolerance]
                                # Para presupuestos altos, elegir el mejor rating (no el más barato)
                                if is_high_budget:
                                    selected = max(top_rated, key=lambda x: x['predicted_rating'])
                                else:
                                    # Entre los mejores, elegir el más barato
                                    selected = min(top_rated, key=lambda x: x['price'])
                            else:
                                # Si no hay de gama media/alta, usar mejor rating disponible
                                best_rating = max(c['predicted_rating'] for c in affordable_candidates)
                                top_rated = [c for c in affordable_candidates 
                                           if c['predicted_rating'] >= best_rating * 0.95]
                                # Para presupuestos altos, elegir el mejor rating
                                if is_high_budget:
                                    selected = max(top_rated, key=lambda x: x['predicted_rating'])
                                else:
                                    selected = min(top_rated, key=lambda x: x['price'])
                    else:
                        # Para otros componentes críticos: maximizar rating
                        # Para RAM en edición con presupuesto alto, priorizar 32GB
                        if is_high_budget and comp_type == 'RAM' and ('design' in use_cases or 'video_editing' in use_cases):
                            ram_32gb = []
                            for c in affordable_candidates:
                                # Intentar múltiples formas de obtener la capacidad
                                capacity = 0
                                features = c.get('features', {})
                                # Intentar capacity_gb
                                if 'capacity_gb' in features:
                                    capacity = int(features['capacity_gb']) if features['capacity_gb'] else 0
                                # Si no, intentar extraer del nombre
                                elif 'name' in c:
                                    name_upper = c['name'].upper()
                                    if '32GB' in name_upper or '32 GB' in name_upper:
                                        capacity = 32
                                    elif '64GB' in name_upper or '64 GB' in name_upper:
                                        capacity = 64
                                    elif '16GB' in name_upper or '16 GB' in name_upper:
                                        capacity = 16
                                    elif '8GB' in name_upper or '8 GB' in name_upper:
                                        capacity = 8
                                
                                if capacity >= 32:
                                    ram_32gb.append(c)
                            
                            if ram_32gb:
                                # Elegir el mejor rating entre RAM de 32GB+
                                best_rating = max(c['predicted_rating'] for c in ram_32gb)
                                top_rated = [c for c in ram_32gb 
                                           if c['predicted_rating'] >= best_rating * 0.98]
                                # Elegir el más caro (mejor calidad) entre los mejor calificados
                                selected = max(top_rated, key=lambda x: x['price'])
                            else:
                                # Si no hay 32GB, intentar 2 módulos de 16GB
                                ram_16gb = []
                                for c in affordable_candidates:
                                    capacity = 0
                                    features = c.get('features', {})
                                    if 'capacity_gb' in features:
                                        capacity = int(features['capacity_gb']) if features['capacity_gb'] else 0
                                    elif 'name' in c:
                                        name_upper = c['name'].upper()
                                        if '16GB' in name_upper or '16 GB' in name_upper:
                                            capacity = 16
                                        elif '8GB' in name_upper or '8 GB' in name_upper:
                                            capacity = 8
                                
                                    if capacity == 16:
                                        ram_16gb.append(c)
                                
                                # Verificar si podemos usar 2 módulos de 16GB
                                if ram_16gb and 'MOTHERBOARD' in components:
                                    mb = components['MOTHERBOARD']
                                    mb_slots = mb.get('features', {}).get('ram_slots', 4)  # Por defecto 4 slots
                                    # Verificar que tengamos al menos 2 slots disponibles
                                    current_ram_count = sum(1 for k in components.keys() if k.startswith('RAM'))
                                    if mb_slots >= 2 and current_ram_count == 0:
                                        # Calcular precio total de 2 módulos
                                        ram_16gb_with_price = [(c, c['price'] * 2) for c in ram_16gb]
                                        # Filtrar por presupuesto (precio total de 2 módulos)
                                        affordable_dual = [(c, total_price) for c, total_price in ram_16gb_with_price 
                                                          if total_price <= allocated_budget * 1.20]  # Permitir 20% de exceso para 2 módulos
                                        
                                        if affordable_dual:
                                            # Elegir el mejor rating
                                            best_rating = max(c['predicted_rating'] for c, _ in affordable_dual)
                                            top_rated = [(c, total_price) for c, total_price in affordable_dual 
                                                        if c['predicted_rating'] >= best_rating * 0.98]
                                            # Elegir el más caro (mejor calidad) entre los mejor calificados
                                            best_ram_16gb, total_price_2x = max(top_rated, key=lambda x: x[1])
                                            
                                            # Seleccionar 2 módulos idénticos
                                            selected = best_ram_16gb
                                            # Marcar que necesitamos 2 módulos
                                            selected['_quantity'] = 2
                                            selected['_total_price'] = total_price_2x
                                            print(f"   ℹ️  {comp_type:12s}: Seleccionando 2x {best_ram_16gb['name'][:30]} (32GB total)")
                                        else:
                                            # Si 2 módulos no caben en presupuesto, usar lógica normal
                                            selected = None
                                    else:
                                        # No hay suficientes slots o ya hay RAM seleccionada
                                        selected = None
                                else:
                                    # No hay RAM de 16GB o no hay motherboard seleccionada aún
                                    selected = None
                                
                                if not selected:
                                    # Si no hay 32GB ni 2x16GB, usar lógica normal pero priorizar las de mayor capacidad
                                    # Primero intentar encontrar las de mayor capacidad disponible
                                    ram_by_capacity = []
                                    for c in affordable_candidates:
                                        capacity = 0
                                        features = c.get('features', {})
                                        if 'capacity_gb' in features:
                                            capacity = int(features['capacity_gb']) if features['capacity_gb'] else 0
                                        elif 'name' in c:
                                            name_upper = c['name'].upper()
                                            if '32GB' in name_upper or '32 GB' in name_upper:
                                                capacity = 32
                                            elif '64GB' in name_upper or '64 GB' in name_upper:
                                                capacity = 64
                                            elif '16GB' in name_upper or '16 GB' in name_upper:
                                                capacity = 16
                                            elif '8GB' in name_upper or '8 GB' in name_upper:
                                                capacity = 8
                                        ram_by_capacity.append((c, capacity))
                                    
                                    # Ordenar por capacidad (mayor primero)
                                    ram_by_capacity.sort(key=lambda x: x[1], reverse=True)
                                    max_capacity = ram_by_capacity[0][1] if ram_by_capacity else 0
                                    
                                    # Si hay RAM de 16GB o más, priorizar las de mayor capacidad
                                    if max_capacity >= 16:
                                        high_capacity_rams = [c for c, cap in ram_by_capacity if cap >= 16]
                                        best_rating = max(c['predicted_rating'] for c in high_capacity_rams)
                                        tolerance = 0.98 if is_high_budget else 0.95
                                        top_rated = [c for c in high_capacity_rams 
                                                   if c['predicted_rating'] >= best_rating * tolerance]
                                        if is_high_budget:
                                            selected = max(top_rated, key=lambda x: x['price'])
                                        else:
                                            selected = min(top_rated, key=lambda x: x['price'])
                                    else:
                                        # Lógica normal
                                        best_rating = max(c['predicted_rating'] for c in affordable_candidates)
                                        tolerance = 0.98 if is_high_budget else 0.95
                                        top_rated = [c for c in affordable_candidates 
                                                   if c['predicted_rating'] >= best_rating * tolerance]
                                        if is_high_budget:
                                            selected = max(top_rated, key=lambda x: x['price'])
                                        else:
                                            selected = min(top_rated, key=lambda x: x['price'])
                        else:
                            # Lógica normal para otros componentes
                            best_rating = max(c['predicted_rating'] for c in affordable_candidates)
                            # Para presupuestos altos, ser más estricto
                            tolerance = 0.98 if is_high_budget else 0.95
                            top_rated = [c for c in affordable_candidates 
                                       if c['predicted_rating'] >= best_rating * tolerance]
                            # Para presupuestos altos, elegir el mejor rating Y el más caro
                            if is_high_budget:
                                best_rated = max(top_rated, key=lambda x: x['predicted_rating'])
                                # Si hay varios con el mismo rating, elegir el más caro (mejor gama)
                                same_rating = [c for c in top_rated if c['predicted_rating'] >= best_rated['predicted_rating'] * 0.99]
                                if len(same_rating) > 1:
                                    selected = max(same_rating, key=lambda x: x['price'])
                                else:
                                    selected = best_rated
                            else:
                                # Entre los mejores, elegir el más barato
                                selected = min(top_rated, key=lambda x: x['price'])
                else:
                    # Para componentes no críticos: balance rating/precio
                    if is_low_budget:
                        # Para presupuestos bajos: priorizar precio pero mantener calidad mínima
                        quality_candidates = [c for c in affordable_candidates if c['predicted_rating'] >= 2.5]
                        if quality_candidates:
                            selected = min(quality_candidates, key=lambda x: x['price'])
                        else:
                            # Si no hay con calidad mínima, usar mejor rating disponible
                            selected = max(affordable_candidates, key=lambda x: x['predicted_rating'])
                    else:
                        # Para presupuestos normales: balance entre rating y precio
                        best_rating = max(c['predicted_rating'] for c in affordable_candidates)
                        top_rated = [c for c in affordable_candidates 
                                   if c['predicted_rating'] >= best_rating * 0.90]  # 10% tolerancia
                        selected = min(top_rated, key=lambda x: x['price'])
            else:
                # Si no hay dentro del presupuesto, buscar en compatibles pero más caros
                if compatible_candidates:
                    # Ordenar compatibles por precio
                    compatible_candidates.sort(key=lambda x: x['price'])
                    
                    # Si es componente requerido, considerar tomar el más barato compatible
                    if comp_type in required_components:
                        cheapest_compatible = compatible_candidates[0]
                        # Para presupuestos bajos, ser más estricto
                        max_total_excess = 1.05 if is_low_budget else 1.15
                        # Verificar si podemos ajustar el presupuesto
                        if cheapest_compatible['price'] <= budget * max_total_excess:
                            selected = cheapest_compatible
                        else:
                            # Si es demasiado caro, intentar ajustar otros componentes
                            print(f"   ⚠️  {comp_type:12s}: Componente compatible muy caro (S/ {cheapest_compatible['price']:.0f})")
                            # Para presupuestos bajos, no seleccionar si excede mucho
                            if is_low_budget and cheapest_compatible['price'] > budget * 1.10:
                                print(f"   ⊗ {comp_type:12s}: Omitido (excede demasiado para presupuesto bajo)")
                                skipped_components.append(comp_type)
                                continue
                            # Continuar para intentar ajustar en iteraciones posteriores
                            selected = cheapest_compatible
                    else:
                        # Componente opcional - omitir si es muy caro
                        print(f"   ⊗ {comp_type:12s}: Omitido (excede presupuesto)")
                        skipped_components.append(comp_type)
                        continue
                else:
                    # No hay componentes compatibles - esto no debería pasar si el filtro funciona
                    print(f"   ❌ {comp_type:12s}: Sin componentes compatibles disponibles")
                    if comp_type in required_components:
                        print(f"   ⚠️  ADVERTENCIA: Componente requerido sin opciones compatibles")
                    skipped_components.append(comp_type)
                    continue
            
            if selected:
                # Manejar múltiples módulos de RAM (2x 16GB = 32GB)
                quantity = selected.get('_quantity', 1)
                if quantity > 1:
                    # Guardar el primer módulo como 'RAM' y el segundo como 'RAM_2'
                    ram_copy = selected.copy()
                    ram_copy.pop('_quantity', None)  # Remover flag interno
                    ram_copy.pop('_total_price', None)  # Remover precio total
                    components[comp_type] = ram_copy
                    components[f'{comp_type}_2'] = ram_copy.copy()
                    
                    # Usar el precio total de los 2 módulos
                    total_price_ram = selected.get('_total_price', selected['price'] * quantity)
                    total_cost += total_price_ram
                    remaining_budget = budget - total_cost
                    
                    over_budget = total_price_ram > allocated_budget
                    way_over = total_price_ram > max_price
                    
                    if way_over:
                        marker = "🔴"
                    elif over_budget:
                        marker = "⚠️"
                    else:
                        marker = "✅"
                    
                    # Calcular capacidad total
                    capacity = 0
                    features = selected.get('features', {})
                    if 'capacity_gb' in features:
                        capacity = int(features['capacity_gb']) if features['capacity_gb'] else 0
                    elif 'name' in selected:
                        name_upper = selected['name'].upper()
                        if '16GB' in name_upper or '16 GB' in name_upper:
                            capacity = 16
                        elif '8GB' in name_upper or '8 GB' in name_upper:
                            capacity = 8
                    total_capacity = capacity * quantity
                    
                    print(f"   {marker} {comp_type:12s}: {quantity}x {selected['name'][:28]:28s} ({total_capacity}GB total) | S/ {total_price_ram:6.0f} | Rating: {selected['predicted_rating']:.2f}")
                else:
                    # Componente único (comportamiento normal)
                    components[comp_type] = selected
                    total_cost += selected['price']
                    remaining_budget = budget - total_cost
                    
                    over_budget = selected['price'] > allocated_budget
                    way_over = selected['price'] > max_price
                    
                    if way_over:
                        marker = "🔴"
                    elif over_budget:
                        marker = "⚠️"
                    else:
                        marker = "✅"
                    
                    print(f"   {marker} {comp_type:12s}: {selected['name'][:35]:35s} | S/ {selected['price']:6.0f} | Rating: {selected['predicted_rating']:.2f}")
        
        # 5. Ajuste post-selección más agresivo si excede presupuesto
        # Para presupuestos bajos, ser más estricto
        max_excess = 1.03 if is_low_budget else 1.05  # 3% para bajos, 5% para normales
        max_iterations = 8 if is_low_budget else 5  # Más iteraciones para presupuestos bajos
        
        iteration = 0
        
        while total_cost > budget * max_excess and iteration < max_iterations:
            iteration += 1
            print(f"\n⚠️  Ajustando configuración (iteración {iteration}) - Total: S/ {total_cost:.0f} (Presupuesto: S/ {budget:.0f})...")
            
            # Ordenar componentes por exceso de presupuesto (mayor exceso primero)
            components_by_excess = []
            for comp_type, comp in components.items():
                allocated = budget * budget_distribution.get(comp_type, 0.10)
                excess = comp['price'] - allocated
                excess_ratio = excess / allocated if allocated > 0 else 0
                components_by_excess.append((comp_type, comp, excess_ratio))
            
            components_by_excess.sort(key=lambda x: x[2], reverse=True)
            
            adjusted = False
            target_excess = 1.02 if is_low_budget else 1.05  # 2% para bajos, 5% para normales
            for comp_type, current_comp, excess_ratio in components_by_excess:
                if total_cost <= budget * target_excess:  # Ya está OK
                    break
                
                # Para gaming, NO degradar CPUs/GPUs de gama media/alta a gama baja
                is_gaming_critical = 'gaming' in use_cases and comp_type in ['CPU', 'GPU']
                if is_gaming_critical:
                    current_name = current_comp['name'].upper()
                    is_current_mid_high = any(x in current_name for x in ['RYZEN 5', 'RYZEN 7', 'RYZEN 9', 
                                                                          'CORE I5', 'CORE I7', 'CORE I9'])
                    # Si el componente actual es de gama media/alta, NO degradarlo
                    if is_current_mid_high:
                        print(f"   ⚠️  {comp_type:12s}: Manteniendo componente de gama media/alta (no se degradará)")
                        continue  # Saltar este componente, buscar otros para ajustar
                
                # Buscar alternativa más barata pero compatible
                candidates = self.recommender.recommend(
                    profile_id=profile_id,
                    model_type=model_type,
                    top_k=50,
                    component_type=comp_type
                )
                
                compatible = self.filter_compatible_components(candidates, components, comp_type)
                # NUNCA usar componentes incompatibles - si no hay compatibles, buscar más
                if not compatible:
                    # Intentar obtener más candidatos
                    more_candidates = self.recommender.recommend(
                        profile_id=profile_id,
                        model_type=model_type,
                        top_k=100,
                        component_type=comp_type
                    )
                    compatible = self.filter_compatible_components(more_candidates, components, comp_type)
                
                # Para gaming, filtrar componentes de gama baja si estamos ajustando CPU/GPU
                if is_gaming_critical:
                    compatible = [c for c in compatible 
                                if not any(x in c['name'].upper() for x in ['RYZEN 3', 'CORE I3', 'ATHLON', 'PENTIUM', 'CELERON'])]
                    if not compatible:
                        print(f"   ⚠️  {comp_type:12s}: No hay alternativas de gama media/alta más baratas (manteniendo actual)")
                        continue  # Saltar este componente
                
                # Buscar alternativa que reduzca el costo
                # Para presupuestos bajos, ser más agresivo en la reducción
                reduction_target = 0.80 if is_low_budget else 0.85  # 20% más barato para bajos, 15% para normales
                target_price = current_comp['price'] * reduction_target
                allocated = budget * budget_distribution.get(comp_type, 0.10)
                
                # Ordenar por precio (más barato primero) para presupuestos bajos
                if is_low_budget:
                    compatible.sort(key=lambda x: x['price'])
                
                # Obtener precio actual (puede ser de múltiples módulos)
                current_price = current_comp.get('_total_price', current_comp['price'])
                
                for candidate in compatible:
                    candidate_price = candidate['price']
                    # Preferir componentes dentro del presupuesto asignado
                    if candidate_price <= allocated and candidate_price < current_price:
                        old_price = current_price
                        # Si había múltiples módulos, eliminar RAM_2
                        if comp_type == 'RAM' and f'{comp_type}_2' in components:
                            del components[f'{comp_type}_2']
                        components[comp_type] = candidate
                        savings = old_price - candidate_price
                        total_cost -= savings
                        print(f"   🔽 {comp_type:12s}: Cambiado a opción más económica (S/ {old_price:.0f} → S/ {candidate_price:.0f}, ahorro: S/ {savings:.0f})")
                        adjusted = True
                        break
                    # Si no hay dentro del presupuesto, buscar más barato que el actual
                    elif candidate_price < target_price and candidate_price < current_price:
                        old_price = current_price
                        # Si había múltiples módulos, eliminar RAM_2
                        if comp_type == 'RAM' and f'{comp_type}_2' in components:
                            del components[f'{comp_type}_2']
                        components[comp_type] = candidate
                        savings = old_price - candidate_price
                        total_cost -= savings
                        print(f"   🔽 {comp_type:12s}: Cambiado a opción más económica (S/ {old_price:.0f} → S/ {candidate_price:.0f}, ahorro: S/ {savings:.0f})")
                        adjusted = True
                        break
                    # Para presupuestos bajos, aceptar cualquier reducción significativa
                    elif is_low_budget and candidate_price < current_price * 0.95:  # 5% más barato
                        old_price = current_price
                        # Si había múltiples módulos, eliminar RAM_2
                        if comp_type == 'RAM' and f'{comp_type}_2' in components:
                            del components[f'{comp_type}_2']
                        components[comp_type] = candidate
                        savings = old_price - candidate_price
                        total_cost -= savings
                        print(f"   🔽 {comp_type:12s}: Cambiado a opción más económica (S/ {old_price:.0f} → S/ {candidate_price:.0f}, ahorro: S/ {savings:.0f})")
                        adjusted = True
                        break
                
                if adjusted:
                    break
            
            if not adjusted:
                # Si no se pudo ajustar más, salir
                break
        
        # 6. Validar compatibilidad
        compatibility = self.validate_compatibility(components)
        
        # 7. Resumen
        remaining = budget - total_cost
        budget_compliance = (total_cost / budget * 100) if budget else 0
        # Para presupuestos bajos, máximo 3% de exceso; para normales, 5%
        max_allowed_excess = 1.03 if is_low_budget else 1.05
        within_budget = total_cost <= budget * max_allowed_excess
        
        print(f"\n{'='*60}")
        print(f"💰 RESUMEN FINANCIERO:")
        print(f"   Presupuesto: S/ {budget:,.0f}")
        print(f"   Total:       S/ {total_cost:,.0f}")
        print(f"   Diferencia:  S/ {remaining:,.0f}")
        print(f"   Uso:         {budget_compliance:.1f}%")
        
        if skipped_components:
            print(f"   ⊗ Omitidos:  {', '.join(skipped_components)}")
        
        if within_budget:
            print(f"   ✅ Dentro de presupuesto aceptable")
        else:
            print(f"   ⚠️  Excede presupuesto en S/ {abs(remaining):,.0f}")
        
        print(f"\n🔧 COMPATIBILIDAD:")
        if compatibility['is_valid']:
            print(f"   ✅ Compatible")
        else:
            print(f"   ❌ Errores:")
            for error in compatibility['errors']:
                print(f"      {error}")
        
        if compatibility['warnings']:
            print(f"   ⚠️  Advertencias:")
            for warning in compatibility['warnings']:
                print(f"      {warning}")
        
        print(f"{'='*60}\n")
        
        return {
            'user_input': {
                'message': user_message,
                'parsed': parsed
            },
            'configuration': components,
            'costs': {
                'budget': budget,
                'total': total_cost,
                'remaining': remaining,
                'compliance_percentage': budget_compliance,
                'within_budget': within_budget
            },
            'compatibility': compatibility,
            'skipped_components': skipped_components,
            'model_used': model_type
        }


    def compare_models(self, user_message: str) -> Dict:
        """
        Compara recomendaciones de ambos modelos (NCF vs Rules)
        """
        print("\n" + "="*60)
        print("🔬 COMPARACIÓN DE MODELOS")
        print("="*60)
        
        # Generar con ambos modelos
        print("\n📊 Generando configuración con modelo NCF...")
        config_ncf = self.build_pc_configuration(user_message, model_type='ncf')
        
        print("\n📊 Generando configuración con modelo de Reglas...")
        config_rules = self.build_pc_configuration(user_message, model_type='rule')
        
        return {
            'ncf': config_ncf,
            'rules': config_rules
        }

# ==================== TEST ====================


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TEST DEL PC BUILDER SERVICE (OPTIMIZADO)")
    print("="*60)
    
    service = PCBuilderService()
    
    # Test 1: Gamer
    test1 = "Quiero una PC para jugar Valorant, tengo 2000 soles"
    config1 = service.build_pc_configuration(test1, model_type='rule')
    
    # Test 2: Developer
    test2 = "PC para programar Python, presupuesto 1500 soles"
    config2 = service.build_pc_configuration(test2, model_type='rule')
    
    # Test 3: Office
    test3 = "Computadora para oficina, Excel y Word, 900 soles"
    config3 = service.build_pc_configuration(test3, model_type='rule')
    
    print("\n" + "="*60)
    print("✅ TESTS COMPLETADOS")
    print("="*60 + "\n")
    print("="*60 + "\n")