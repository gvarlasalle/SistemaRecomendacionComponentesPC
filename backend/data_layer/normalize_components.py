# backend/data_layer/normalize_components.py
"""
NORMALIZACIÓN ROBUSTA del dataset
- Maneja valores N/A y vacíos
- Extrae features técnicos objetivos
- Compatible con specs inconsistentes
- Prepara datos para ML
"""

import json
import re
from typing import Dict, Any, Optional

def extract_numeric(text: str, default: int = 0) -> int:
    """Extrae primer número de un texto, maneja N/A"""
    if not text or text in ['N/A', 'n/a', 'No aplica', 'No incluye']:
        return default
    match = re.search(r'\d+', str(text))
    return int(match.group()) if match else default

def extract_float(text: str, default: float = 0.0) -> float:
    """Extrae primer número decimal, maneja N/A"""
    if not text or text in ['N/A', 'n/a', 'No aplica', 'No incluye']:
        return default
    match = re.search(r'\d+\.?\d*', str(text))
    return float(match.group()) if match else default

def clean_text(text: str) -> str:
    """Limpia texto, convierte N/A a string vacío"""
    if not text or text in ['N/A', 'n/a', 'No aplica', 'No incluye', 'Unknown']:
        return ''
    return str(text).strip()

def safe_get(dictionary: Dict, *keys, default: Any = '') -> Any:
    """Obtiene valor de dict con múltiples keys posibles"""
    for key in keys:
        if key in dictionary and dictionary[key]:
            value = dictionary[key]
            if value not in ['N/A', 'n/a', 'No aplica', 'No incluye']:
                return value
    return default

# ==================== NORMALIZADORES POR TIPO ====================

def normalize_cpu(component: Dict) -> Dict:
    """Normaliza CPU - maneja specs variables"""
    specs = component.get('specs', {})
    name = component.get('name', '').upper()
    price = component.get('regular_price', 0)
    
    # Socket (campo crítico)
    socket = clean_text(safe_get(specs, 'socket', 'zócalo', 'Socket'))
    
    # Cores (puede estar en varios formatos)
    cores_str = safe_get(specs, 'cantidad_núcleos', 'nucleos', 'cores', 'núcleos')
    cores = extract_numeric(cores_str)
    
    # Si no encontró cores en specs, intentar del nombre
    if cores == 0:
        if 'QUAD CORE' in name or '4 CORE' in name or '4 NÚCLEOS' in name:
            cores = 4
        elif '6 CORE' in name or '6 NÚCLEOS' in name:
            cores = 6
        elif '8 CORE' in name or '8 NÚCLEOS' in name:
            cores = 8
        elif '10 CORE' in name or '10 NÚCLEOS' in name:
            cores = 10
        elif '12 CORE' in name or '12 NÚCLEOS' in name:
            cores = 12
        elif '16 CORE' in name or '16 NÚCLEOS' in name:
            cores = 16
    
    # Frecuencia base
    freq_str = safe_get(specs, 'velocidad', 'frecuencia', 'frequency')
    base_freq_ghz = extract_float(freq_str)
    
    # TDP
    tdp_str = safe_get(specs, 'tdp_procesador', 'tdp', 'consumo', 'potencia')
    tdp_watts = extract_numeric(tdp_str)
    
    # Cache L3
    cache_str = safe_get(specs, 'cache_l3', 'cache_l2', 'cache')
    cache_mb = extract_numeric(cache_str)
    
    # GPU integrada
    igpu_str = safe_get(specs, 'gpu_integrado', 'grafico_integrado', 'integrated_gpu')
    has_igpu = igpu_str.lower() in ['sí', 'si', 'yes', 'incluye']
    
    # Marca (AMD vs Intel)
    if 'INTEL' in name or any(x in name for x in ['I3', 'I5', 'I7', 'I9', 'CORE']):
        brand = 'Intel'
    elif 'AMD' in name or 'RYZEN' in name:
        brand = 'AMD'
    else:
        brand = 'Unknown'
    
    # Serie del procesador
    series = 'Unknown'
    if brand == 'AMD':
        if 'RYZEN 9' in name:
            series = 'Ryzen 9'
        elif 'RYZEN 7' in name:
            series = 'Ryzen 7'
        elif 'RYZEN 5' in name:
            series = 'Ryzen 5'
        elif 'RYZEN 3' in name:
            series = 'Ryzen 3'
    elif brand == 'Intel':
        if 'I9' in name or 'CORE I9' in name:
            series = 'Core i9'
        elif 'I7' in name or 'CORE I7' in name:
            series = 'Core i7'
        elif 'I5' in name or 'CORE I5' in name:
            series = 'Core i5'
        elif 'I3' in name or 'CORE I3' in name:
            series = 'Core i3'
    
    # Performance tier (basado en specs, no en uso)
    if cores >= 12 or series in ['Ryzen 9', 'Core i9']:
        performance_tier = 'enthusiast'
    elif cores >= 8 or series in ['Ryzen 7', 'Core i7']:
        performance_tier = 'high'
    elif cores >= 6 or series in ['Ryzen 5', 'Core i5']:
        performance_tier = 'mid'
    else:
        performance_tier = 'budget'
    
    return {
        'socket': socket,
        'cores': cores,
        'base_frequency_ghz': base_freq_ghz,
        'tdp_watts': tdp_watts,
        'cache_mb': cache_mb,
        'has_integrated_gpu': has_igpu,
        'brand': brand,
        'series': series,
        'performance_tier': performance_tier,
        'price_soles': price
    }

def normalize_gpu(component: Dict) -> Dict:
    """Normaliza GPU - maneja specs variables"""
    specs = component.get('specs', {})
    name = component.get('name', '').upper()
    price = component.get('regular_price', 0)
    
    # Marca
    if 'NVIDIA' in name or 'RTX' in name or 'GTX' in name or 'GEFORCE' in name:
        brand = 'NVIDIA'
    elif 'AMD' in name or 'RADEON' in name or 'RX' in name:
        brand = 'AMD'
    elif 'INTEL' in name or 'ARC' in name:
        brand = 'Intel'
    else:
        brand = 'Unknown'
    
    # VRAM
    vram_str = safe_get(specs, 'memoria', 'vram', 'memoria_video', 'video_memory')
    vram_gb = extract_numeric(vram_str)
    
    # Si no encontró en specs, buscar en nombre
    if vram_gb == 0:
        vram_match = re.search(r'(\d+)\s*GB', name)
        if vram_match:
            vram_gb = int(vram_match.group(1))
    
    # Modelo específico
    model = 'Unknown'
    if 'RTX 4090' in name:
        model = 'RTX 4090'
    elif 'RTX 4080' in name:
        model = 'RTX 4080'
    elif 'RTX 4070 TI' in name or 'RTX 4070TI' in name:
        model = 'RTX 4070 Ti'
    elif 'RTX 4070' in name:
        model = 'RTX 4070'
    elif 'RTX 4060 TI' in name or 'RTX 4060TI' in name:
        model = 'RTX 4060 Ti'
    elif 'RTX 4060' in name:
        model = 'RTX 4060'
    elif 'RTX 3060' in name:
        model = 'RTX 3060'
    elif 'RTX 3050' in name:
        model = 'RTX 3050'
    elif 'RX 7900 XTX' in name:
        model = 'RX 7900 XTX'
    elif 'RX 7900 XT' in name:
        model = 'RX 7900 XT'
    elif 'RX 7800 XT' in name:
        model = 'RX 7800 XT'
    elif 'RX 7700 XT' in name:
        model = 'RX 7700 XT'
    elif 'RX 7600' in name:
        model = 'RX 7600'
    elif 'GTX 1660' in name or 'GTX1660' in name:
        model = 'GTX 1660'
    elif 'GTX 1650' in name or 'GTX1650' in name:
        model = 'GTX 1650'
    
    # Performance tier
    if price > 3000 or vram_gb >= 16:
        performance_tier = 'enthusiast'
    elif price > 1500 or vram_gb >= 12:
        performance_tier = 'high'
    elif price > 700 or vram_gb >= 8:
        performance_tier = 'mid'
    else:
        performance_tier = 'budget'
    
    # TDP (consumo)
    tdp_str = safe_get(specs, 'tdp', 'consumo', 'potencia', 'power')
    tdp_watts = extract_numeric(tdp_str)
    
    return {
        'brand': brand,
        'model': model,
        'vram_gb': vram_gb,
        'tdp_watts': tdp_watts,
        'performance_tier': performance_tier,
        'price_soles': price
    }

def normalize_ram(component: Dict) -> Dict:
    """Normaliza RAM - maneja specs variables"""
    specs = component.get('specs', {})
    name = component.get('name', '').upper()
    price = component.get('regular_price', 0)
    
    # Tipo de memoria
    tipo_str = safe_get(specs, 'tipo_de_memoria', 'tipo', 'memory_type', 'tipo_memoria')
    
    # Detectar DDR del nombre si no está en specs
    if not tipo_str or tipo_str == '':
        if 'DDR5' in name:
            tipo_str = 'DDR5'
        elif 'DDR4' in name:
            tipo_str = 'DDR4'
        elif 'DDR3' in name:
            tipo_str = 'DDR3'
    
    # Normalizar tipo
    if 'DDR5' in tipo_str.upper():
        ram_type = 'DDR5'
    elif 'DDR4' in tipo_str.upper():
        ram_type = 'DDR4'
    elif 'DDR3' in tipo_str.upper():
        ram_type = 'DDR3'
    else:
        ram_type = 'Unknown'
    
    # Capacidad
    capacity_str = safe_get(specs, 'capacidad', 'capacity', 'tamaño')
    capacity_gb = extract_numeric(capacity_str)
    
    # Si no encontró en specs, buscar en nombre
    if capacity_gb == 0:
        cap_match = re.search(r'(\d+)\s*GB', name)
        if cap_match:
            capacity_gb = int(cap_match.group(1))
    
    # Frecuencia
    freq_str = safe_get(specs, 'frecuencia', 'frequency', 'velocidad')
    frequency_mhz = extract_numeric(freq_str)
    
    # Si no encontró en specs, buscar en nombre
    if frequency_mhz == 0:
        freq_match = re.search(r'(\d{4,5})\s*MH?Z', name)
        if freq_match:
            frequency_mhz = int(freq_match.group(1))
    
    # Latencia CAS
    latency_str = safe_get(specs, 'latencia', 'latency', 'cas')
    latency_cas = extract_numeric(latency_str)
    
    return {
        'ram_type': ram_type,
        'capacity_gb': capacity_gb,
        'frequency_mhz': frequency_mhz,
        'latency_cas': latency_cas,
        'price_soles': price
    }

def normalize_motherboard(component: Dict) -> Dict:
    """Normaliza Motherboard - maneja specs variables"""
    specs = component.get('specs', {})
    name = component.get('name', '').upper()
    price = component.get('regular_price', 0)
    
    # Socket (crítico para compatibilidad)
    socket = clean_text(safe_get(specs, 'socket', 'zócalo', 'Socket', 'cpu_socket'))
    
    # Si no está en specs, buscar en nombre
    if not socket:
        if 'AM4' in name:
            socket = 'Socket AM4'
        elif 'AM5' in name:
            socket = 'Socket AM5'
        elif 'LGA 1700' in name or 'LGA1700' in name:
            socket = 'Socket LGA 1700'
        elif 'LGA 1200' in name or 'LGA1200' in name:
            socket = 'Socket LGA 1200'
        elif 'LGA 1851' in name or 'LGA1851' in name:
            socket = 'Socket LGA 1851'
    
    # Tipo de RAM soportado
    ram_str = safe_get(specs, 'tipo_de_memoria', 'memoria', 'ram_type', 'memory_type')
    
    # Detectar del nombre si no está en specs
    if not ram_str:
        if 'DDR5' in name:
            ram_str = 'DDR5'
        elif 'DDR4' in name:
            ram_str = 'DDR4'
        elif 'DDR3' in name:
            ram_str = 'DDR3'
    
    if 'DDR5' in ram_str.upper():
        supported_ram_type = 'DDR5'
    elif 'DDR4' in ram_str.upper():
        supported_ram_type = 'DDR4'
    elif 'DDR3' in ram_str.upper():
        supported_ram_type = 'DDR3'
    else:
        supported_ram_type = 'Unknown'
    
    # Form factor
    form_str = safe_get(specs, 'formato', 'form_factor', 'tamaño')
    
    # Detectar del nombre si no está en specs
    if not form_str:
        if 'MATX' in name or 'M-ATX' in name or 'MICRO ATX' in name:
            form_str = 'mATX'
        elif 'MINI ITX' in name or 'MINI-ITX' in name:
            form_str = 'Mini ITX'
        elif 'ATX' in name:
            form_str = 'ATX'
    
    form_factor = clean_text(form_str) or 'ATX'
    
    # Chipset
    chipset = clean_text(safe_get(specs, 'chipset', 'chip'))
    
    return {
        'socket': socket,
        'supported_ram_type': supported_ram_type,
        'form_factor': form_factor,
        'chipset': chipset,
        'price_soles': price
    }

def normalize_storage(component: Dict) -> Dict:
    """Normaliza Storage - maneja specs variables"""
    specs = component.get('specs', {})
    name = component.get('name', '').upper()
    price = component.get('regular_price', 0)
    
    # Capacidad
    capacity_str = safe_get(specs, 'capacidad', 'capacity', 'tamaño')
    capacity_gb = extract_numeric(capacity_str)
    
    # Buscar en nombre si no está en specs
    if capacity_gb == 0:
        # Buscar TB
        tb_match = re.search(r'(\d+)\s*TB', name)
        if tb_match:
            capacity_gb = int(tb_match.group(1)) * 1000
        else:
            # Buscar GB
            gb_match = re.search(r'(\d+)\s*GB', name)
            if gb_match:
                capacity_gb = int(gb_match.group(1))
    
    # Tipo de storage
    if 'NVME' in name or 'M.2' in name or 'M2' in name or 'PCIE' in name:
        storage_type = 'NVME'
    elif 'SSD' in name:
        storage_type = 'SSD'
    elif 'HDD' in name:
        storage_type = 'HDD'
    else:
        storage_type = 'Unknown'
    
    # Velocidad lectura/escritura
    read_str = safe_get(specs, 'velocidad_lectura', 'read_speed', 'lectura')
    read_speed_mbps = extract_numeric(read_str)
    
    write_str = safe_get(specs, 'velocidad_escritura', 'write_speed', 'escritura')
    write_speed_mbps = extract_numeric(write_str)
    
    return {
        'storage_type': storage_type,
        'capacity_gb': capacity_gb,
        'read_speed_mbps': read_speed_mbps,
        'write_speed_mbps': write_speed_mbps,
        'price_soles': price
    }

def normalize_psu(component: Dict) -> Dict:
    """Normaliza PSU - maneja specs variables"""
    specs = component.get('specs', {})
    name = component.get('name', '').upper()
    price = component.get('regular_price', 0)
    
    # Wattage (potencia)
    wattage_str = safe_get(specs, 'potencia', 'wattage', 'power')
    wattage = extract_numeric(wattage_str)
    
    # Buscar en nombre si no está en specs
    if wattage == 0:
        watt_match = re.search(r'(\d+)\s*W', name)
        if watt_match:
            wattage = int(watt_match.group(1))
    
    # Certificación de eficiencia
    cert_str = safe_get(specs, 'certificación', 'certificacion', 'efficiency', 'eficiencia')
    
    # Detectar del nombre también
    combined = (cert_str + ' ' + name).upper()
    
    if 'PLATINUM' in combined or '80 PLUS PLATINUM' in combined:
        efficiency_rating = '80 Plus Platinum'
    elif 'GOLD' in combined or '80 PLUS GOLD' in combined:
        efficiency_rating = '80 Plus Gold'
    elif 'BRONZE' in combined or '80 PLUS BRONZE' in combined:
        efficiency_rating = '80 Plus Bronze'
    elif '80 PLUS' in combined or '80PLUS' in combined:
        efficiency_rating = '80 Plus'
    else:
        efficiency_rating = 'None'
    
    # Modular
    is_modular = any(x in name for x in ['MODULAR', 'FULLY MODULAR', 'SEMI MODULAR', 'SEMI-MODULAR'])
    
    return {
        'wattage': wattage,
        'efficiency_rating': efficiency_rating,
        'is_modular': is_modular,
        'price_soles': price
    }

def normalize_case(component: Dict) -> Dict:
    """Normaliza Case - maneja specs variables"""
    specs = component.get('specs', {})
    name = component.get('name', '').upper()
    price = component.get('regular_price', 0)
    
    # Form factor
    form_str = safe_get(specs, 'formato', 'form_factor', 'tamaño', 'size')
    
    # Detectar del nombre si no está
    if not form_str:
        if 'MINI ITX' in name or 'MINI-ITX' in name:
            form_str = 'Mini ITX'
        elif 'MATX' in name or 'M-ATX' in name or 'MICRO ATX' in name:
            form_str = 'mATX'
        elif 'MID TOWER' in name or 'MID-TOWER' in name:
            form_str = 'ATX'
        elif 'FULL TOWER' in name or 'FULL-TOWER' in name:
            form_str = 'Full Tower'
        elif 'ATX' in name:
            form_str = 'ATX'
    
    form_factor = clean_text(form_str) or 'ATX'
    
    return {
        'form_factor': form_factor,
        'price_soles': price
    }

def normalize_monitor(component: Dict) -> Dict:
    """Normaliza Monitor - maneja specs variables"""
    specs = component.get('specs', {})
    name = component.get('name', '').upper()
    price = component.get('regular_price', 0)
    
    # Tamaño pantalla
    size_str = safe_get(specs, 'tamaño', 'size', 'pulgadas', 'screen_size')
    size_inches = extract_numeric(size_str)
    
    # Buscar en nombre
    if size_inches == 0:
        size_match = re.search(r'(\d+)[\s"]*PULGADAS|(\d+)"', name)
        if size_match:
            size_inches = int(size_match.group(1) or size_match.group(2))
    
    # Resolución
    resolution_str = safe_get(specs, 'resolución', 'resolucion', 'resolution')
    
    if '4K' in (resolution_str + name).upper() or '3840' in resolution_str:
        resolution = '4K'
    elif '2K' in (resolution_str + name).upper() or 'QHD' in (resolution_str + name).upper() or '2560' in resolution_str:
        resolution = '2K'
    elif 'FULL HD' in (resolution_str + name).upper() or '1920' in resolution_str or '1080P' in name:
        resolution = 'Full HD'
    else:
        resolution = 'Unknown'
    
    # Tasa de refresco
    refresh_str = safe_get(specs, 'tasa_refresco', 'refresh_rate', 'hz')
    refresh_rate_hz = extract_numeric(refresh_str)
    
    # Buscar en nombre
    if refresh_rate_hz == 0:
        hz_match = re.search(r'(\d+)\s*HZ', name)
        if hz_match:
            refresh_rate_hz = int(hz_match.group(1))
    
    return {
        'size_inches': size_inches,
        'resolution': resolution,
        'refresh_rate_hz': refresh_rate_hz,
        'price_soles': price
    }

# ==================== MAIN ====================

def normalize_component(component: Dict) -> Dict:
    """Normaliza un componente según su tipo"""
    comp_type = component.get('type')
    
    normalized = component.copy()
    
    # Normalizar según tipo
    if comp_type == 'CPU':
        normalized['features'] = normalize_cpu(component)
    elif comp_type == 'GPU':
        normalized['features'] = normalize_gpu(component)
    elif comp_type == 'RAM':
        normalized['features'] = normalize_ram(component)
    elif comp_type == 'MOTHERBOARD':
        normalized['features'] = normalize_motherboard(component)
    elif comp_type == 'STORAGE':
        normalized['features'] = normalize_storage(component)
    elif comp_type == 'PSU':
        normalized['features'] = normalize_psu(component)
    elif comp_type == 'CASE':
        normalized['features'] = normalize_case(component)
    elif comp_type == 'MONITOR':
        normalized['features'] = normalize_monitor(component)
    else:
        normalized['features'] = {}
    
    # Actualizar compatibility con features clave
    features = normalized['features']
    
    if comp_type == 'CPU':
        normalized['compatibility'] = {
            'socket': features.get('socket', '')
        }
    elif comp_type == 'RAM':
        normalized['compatibility'] = {
            'ram_type': features.get('ram_type', ''),
            'capacity_gb': features.get('capacity_gb', 0)
        }
    elif comp_type == 'MOTHERBOARD':
        normalized['compatibility'] = {
            'socket': features.get('socket', ''),
            'supported_ram_type': features.get('supported_ram_type', ''),
            'form_factor': features.get('form_factor', '')
        }
    elif comp_type == 'PSU':
        normalized['compatibility'] = {
            'wattage': features.get('wattage', 0)
        }
    elif comp_type == 'CASE':
        normalized['compatibility'] = {
            'form_factor': features.get('form_factor', '')
        }
    else:
        normalized['compatibility'] = {}
    
    return normalized

def normalize_dataset(input_file: str, output_file: str):
    """Normaliza todo el dataset"""
    print("\n" + "="*60)
    print("📊 NORMALIZANDO DATASET")
    print("="*60)
    print("🔧 Manejando specs inconsistentes y valores N/A")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        components = json.load(f)
    
    print(f"\n📦 Componentes cargados: {len(components)}")
    
    normalized_components = []
    stats = {}
    errors = []
    
    for i, comp in enumerate(components):
        try:
            normalized = normalize_component(comp)
            normalized_components.append(normalized)
            
            comp_type = comp['type']
            stats[comp_type] = stats.get(comp_type, 0) + 1
            
        except Exception as e:
            errors.append(f"Error en componente {i+1} (ID: {comp.get('id', 'N/A')}): {e}")
    
    # Guardar
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(normalized_components, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Dataset normalizado: {output_file}")
    print(f"📊 Total: {len(normalized_components)} componentes\n")
    
    print("📈 Distribución por tipo:")
    for comp_type in sorted(stats.keys()):
        count = stats[comp_type]
        print(f"   {comp_type:15s}: {count:3d} componentes")
    
    if errors:
        print(f"\n⚠️  Errores encontrados: {len(errors)}")
        for error in errors[:5]:  # Mostrar primeros 5
            print(f"   {error}")
    
    # Ejemplos
    print("\n🔍 Ejemplos de features extraídos:\n")
    
    for comp_type in ['CPU', 'GPU', 'RAM', 'MOTHERBOARD']:
        example = next((c for c in normalized_components if c['type'] == comp_type), None)
        if example:
            print(f"   {comp_type}:")
            print(f"      ID: {example['id']}")
            print(f"      Nombre: {example['name'][:50]}")
            print(f"      Precio: S/ {example['regular_price']}")
            print(f"      Features: {json.dumps(example['features'], indent=10, ensure_ascii=False)}\n")
    
    print("="*60)
    
    return normalized_components

if __name__ == "__main__":
    normalize_dataset(
        input_file='data/components_20251123_213834.json',
        output_file='data/components_normalized.json'
    )