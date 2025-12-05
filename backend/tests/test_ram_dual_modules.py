"""
Script de prueba para verificar la funcionalidad de múltiples módulos de RAM.
Prueba diferentes casos donde algunos necesitan 2x16GB (32GB) y otros no.
"""

import sys
import io

# Configurar salida UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from api.pc_builder_service import PCBuilderService

def analyze_ram_configuration(result):
    """Analiza la configuración de RAM en el resultado"""
    config = result['configuration']
    
    ram_info = {
        'has_ram': 'RAM' in config,
        'has_ram_2': 'RAM_2' in config,
        'modules': [],
        'total_capacity_gb': 0,
        'total_price': 0
    }
    
    if ram_info['has_ram']:
        ram = config['RAM']
        capacity = 0
        
        # Intentar obtener capacidad desde features
        features = ram.get('features', {})
        if 'capacity_gb' in features:
            capacity = int(features['capacity_gb']) if features['capacity_gb'] else 0
        else:
            # Intentar extraer del nombre
            name_upper = ram['name'].upper()
            if '32GB' in name_upper or '32 GB' in name_upper:
                capacity = 32
            elif '16GB' in name_upper or '16 GB' in name_upper:
                capacity = 16
            elif '8GB' in name_upper or '8 GB' in name_upper:
                capacity = 8
        
        ram_info['modules'].append({
            'name': ram['name'],
            'capacity_gb': capacity,
            'price': ram['price'],
            'rating': ram.get('predicted_rating', 0)
        })
        ram_info['total_capacity_gb'] += capacity
        ram_info['total_price'] += ram['price']
        
        if ram_info['has_ram_2']:
            ram_2 = config['RAM_2']
            capacity_2 = 0
            
            features_2 = ram_2.get('features', {})
            if 'capacity_gb' in features_2:
                capacity_2 = int(features_2['capacity_gb']) if features_2['capacity_gb'] else 0
            else:
                name_upper_2 = ram_2['name'].upper()
                if '32GB' in name_upper_2 or '32 GB' in name_upper_2:
                    capacity_2 = 32
                elif '16GB' in name_upper_2 or '16 GB' in name_upper_2:
                    capacity_2 = 16
                elif '8GB' in name_upper_2 or '8 GB' in name_upper_2:
                    capacity_2 = 8
            
            ram_info['modules'].append({
                'name': ram_2['name'],
                'capacity_gb': capacity_2,
                'price': ram_2['price'],
                'rating': ram_2.get('predicted_rating', 0)
            })
            ram_info['total_capacity_gb'] += capacity_2
            ram_info['total_price'] += ram_2['price']
    
    return ram_info

def test_case(service, case_name, user_message, expected_ram_gb=None):
    """Ejecuta un caso de prueba y analiza los resultados"""
    print(f"\n{'='*80}")
    print(f"PRUEBA: {case_name}")
    print(f"{'='*80}")
    print(f"Solicitud: '{user_message}'")
    print(f"{'='*80}\n")
    
    result = service.build_pc_configuration(user_message)
    
    # Analizar RAM
    ram_info = analyze_ram_configuration(result)
    
    print(f"\n{'='*80}")
    print(f"ANÁLISIS DE RAM:")
    print(f"{'='*80}")
    
    if ram_info['has_ram']:
        if ram_info['has_ram_2']:
            print(f"✓ Configuración: {len(ram_info['modules'])} módulos de RAM")
            print(f"  - Módulo 1: {ram_info['modules'][0]['name'][:50]}")
            print(f"    Capacidad: {ram_info['modules'][0]['capacity_gb']}GB | Precio: S/ {ram_info['modules'][0]['price']:.0f}")
            print(f"  - Módulo 2: {ram_info['modules'][1]['name'][:50]}")
            print(f"    Capacidad: {ram_info['modules'][1]['capacity_gb']}GB | Precio: S/ {ram_info['modules'][1]['price']:.0f}")
            print(f"\n  Total: {ram_info['total_capacity_gb']}GB | Precio Total: S/ {ram_info['total_price']:.0f}")
            
            # Verificar que son idénticos
            if ram_info['modules'][0]['name'] == ram_info['modules'][1]['name']:
                print(f"  ✓ Los módulos son idénticos (recomendado)")
            else:
                print(f"  ⚠️  Los módulos NO son idénticos (puede causar problemas)")
        else:
            print(f"✓ Configuración: 1 módulo de RAM")
            print(f"  - {ram_info['modules'][0]['name'][:60]}")
            print(f"    Capacidad: {ram_info['modules'][0]['capacity_gb']}GB | Precio: S/ {ram_info['modules'][0]['price']:.0f}")
            print(f"\n  Total: {ram_info['total_capacity_gb']}GB | Precio Total: S/ {ram_info['total_price']:.0f}")
        
        if expected_ram_gb:
            if ram_info['total_capacity_gb'] >= expected_ram_gb:
                print(f"\n  ✓ Capacidad adecuada: {ram_info['total_capacity_gb']}GB >= {expected_ram_gb}GB esperados")
            else:
                print(f"\n  ⚠️  Capacidad insuficiente: {ram_info['total_capacity_gb']}GB < {expected_ram_gb}GB esperados")
    else:
        print(f"✗ No se seleccionó RAM")
    
    # Resumen financiero
    costs = result['costs']
    print(f"\n{'='*80}")
    print(f"RESUMEN FINANCIERO:")
    print(f"{'='*80}")
    print(f"Presupuesto: S/ {costs['budget']:,.0f}")
    print(f"Total:       S/ {costs['total']:,.0f}")
    print(f"Uso:         {costs['compliance_percentage']:.1f}%")
    
    if ram_info['has_ram']:
        ram_percentage = (ram_info['total_price'] / costs['total'] * 100) if costs['total'] > 0 else 0
        print(f"\nRAM:")
        print(f"  Precio: S/ {ram_info['total_price']:.0f} ({ram_percentage:.1f}% del total)")
        print(f"  Capacidad: {ram_info['total_capacity_gb']}GB")
    
    print(f"{'='*80}\n")
    
    return {
        'case_name': case_name,
        'ram_info': ram_info,
        'costs': costs,
        'expected_ram_gb': expected_ram_gb,
        'meets_expectation': ram_info['total_capacity_gb'] >= expected_ram_gb if expected_ram_gb else True
    }

def main():
    print("\n" + "="*80)
    print("PRUEBA: Sistema de Múltiples Módulos de RAM")
    print("="*80)
    
    service = PCBuilderService()
    
    test_cases = [
        {
            'name': 'Presupuesto Alto - Diseño + Edición + Gaming + Streaming (32GB esperados)',
            'message': 'quiero una pc para diseño gráfico, edición de videos, jugar y hacer streams mi presupuesto es de 6000 soles',
            'expected_ram': 32
        },
        {
            'name': 'Gaming Normal (16GB suficientes)',
            'message': 'Quiero una PC para jugar Valorant, tengo 2000 soles',
            'expected_ram': 16  # 16GB debería ser suficiente, no necesariamente 32GB
        },
        {
            'name': 'Presupuesto Bajo - Gaming (8-16GB)',
            'message': 'Quiero una PC para jugar, tengo solo 800 soles',
            'expected_ram': 8  # Mínimo 8GB para gaming básico
        },
        {
            'name': 'Desarrollo/Programación (16GB puede ser suficiente, 32GB ideal)',
            'message': 'PC para programar Python y machine learning, 1800 soles',
            'expected_ram': 16  # 16GB puede funcionar, 32GB sería mejor pero puede no caber en presupuesto
        },
        {
            'name': 'Oficina (8GB suficientes)',
            'message': 'Computadora para oficina, Excel y Word, 900 soles',
            'expected_ram': 8  # 8GB es suficiente para oficina
        },
        {
            'name': 'Gaming 4K Alto Rendimiento (32GB ideal pero 16GB puede ser suficiente)',
            'message': 'PC para gaming de alto rendimiento, quiero jugar juegos AAA en 4K, tengo 5000 soles',
            'expected_ram': 16  # 16GB puede funcionar para gaming, aunque 32GB sería mejor
        },
    ]
    
    results = []
    
    for test_case_data in test_cases:
        result = test_case(
            service,
            test_case_data['name'],
            test_case_data['message'],
            test_case_data.get('expected_ram')
        )
        results.append(result)
    
    # Resumen final
    print("\n" + "="*80)
    print("RESUMEN DE PRUEBAS")
    print("="*80)
    
    for result in results:
        status = "✓" if result['meets_expectation'] else "✗"
        modules = "2 módulos" if result['ram_info']['has_ram_2'] else "1 módulo"
        print(f"{status} {result['case_name']}")
        print(f"   RAM: {result['ram_info']['total_capacity_gb']}GB ({modules})")
        if result['expected_ram_gb']:
            print(f"   Esperado: {result['expected_ram_gb']}GB")
        print()
    
    print("="*80)
    print("✓ PRUEBAS COMPLETADAS")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()

