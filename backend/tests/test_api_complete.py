# backend/test_api_complete.py
"""
Suite completa de pruebas para la API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_separator(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_1_health():
    """Test: Health check"""
    print_separator("TEST 1: Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()
    
    print(f"✓ Status Code: {response.status_code}")
    print(f"✓ API Status: {data['status']}")
    print(f"\nServicios activos:")
    for service, status in data['services'].items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {service}")
    
    assert response.status_code == 200
    assert data['status'] == 'healthy'
    print("\n✅ Test 1 PASSED")

def test_2_chat_gamer():
    """Test: Parse mensaje de gamer"""
    print_separator("TEST 2: Chat Parser - Gamer")
    
    payload = {
        "message": "Quiero una PC para jugar Valorant y Cyberpunk, tengo 2200 soles"
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    data = response.json()
    
    print(f"✓ Status Code: {response.status_code}")
    print(f"\nMensaje: {payload['message']}")
    print(f"\nResultado del parsing:")
    print(f"  Presupuesto: S/ {data['parsed_data']['budget']}")
    print(f"  Perfil sugerido: {data['suggested_profile']}")
    print(f"  Casos de uso: {', '.join(data['parsed_data']['use_cases'])}")
    print(f"  Juegos detectados: {', '.join(data['parsed_data']['games'])}")
    print(f"  Nivel: {data['parsed_data']['performance_level']}")
    print(f"  Prioridades: {' > '.join(data['parsed_data']['priorities'])}")
    
    assert response.status_code == 200
    assert data['parsed_data']['budget'] == 2200
    assert 'gaming' in data['parsed_data']['use_cases']
    print("\n✅ Test 2 PASSED")

def test_3_chat_developer():
    """Test: Parse mensaje de desarrollador"""
    print_separator("TEST 3: Chat Parser - Developer")
    
    payload = {
        "message": "Necesito PC para programar Python y Java, 1600 soles"
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    data = response.json()
    
    print(f"✓ Status Code: {response.status_code}")
    print(f"\nMensaje: {payload['message']}")
    print(f"\nResultado:")
    print(f"  Presupuesto: S/ {data['parsed_data']['budget']}")
    print(f"  Perfil: {data['suggested_profile']}")
    print(f"  Software detectado: {', '.join(data['parsed_data']['software'])}")
    
    assert response.status_code == 200
    assert 'development' in data['parsed_data']['use_cases']
    print("\n✅ Test 3 PASSED")

def test_4_recommend_gamer():
    """Test: Recomendación para gamer"""
    print_separator("TEST 4: Recommend - Gamer")
    
    payload = {
        "message": "PC para jugar en calidad alta, 2500 soles",
        "model_type": "rule"
    }
    
    response = requests.post(f"{BASE_URL}/recommend", json=payload)
    data = response.json()
    
    print(f"✓ Status Code: {response.status_code}")
    print(f"\n💰 Costos:")
    print(f"  Presupuesto: S/ {data['costs']['budget']:,.0f}")
    print(f"  Total: S/ {data['costs']['total']:,.0f}")
    print(f"  Uso: {data['costs']['compliance_percentage']:.1f}%")
    
    print(f"\n🛠️  Configuración generada:")
    for comp_type, comp in data['configuration'].items():
        print(f"  {comp_type:12s}: {comp['name'][:45]:45s} S/ {comp['price']:7,.0f}")
    
    print(f"\n🔧 Compatibilidad:")
    print(f"  Valid: {data['compatibility']['is_valid']}")
    if data['compatibility']['errors']:
        print(f"  Errores: {len(data['compatibility']['errors'])}")
    if data['compatibility']['warnings']:
        print(f"  Advertencias: {len(data['compatibility']['warnings'])}")
    
    assert response.status_code == 200
    assert 'configuration' in data
    print("\n✅ Test 4 PASSED")

def test_5_profiles():
    """Test: Listar perfiles"""
    print_separator("TEST 5: List Profiles")
    
    response = requests.get(f"{BASE_URL}/profiles")
    data = response.json()
    
    print(f"✓ Status Code: {response.status_code}")
    print(f"\nTotal perfiles: {len(data['profiles'])}")
    print(f"\nPerfiles disponibles:")
    
    for profile in data['profiles']:
        budget_min, budget_max = profile['budget_range']
        print(f"  • {profile['name']:30s} | S/ {budget_min:,} - {budget_max:,}")
    
    assert response.status_code == 200
    assert len(data['profiles']) == 9
    print("\n✅ Test 5 PASSED")

def test_6_components_gpu():
    """Test: Filtrar GPUs por precio"""
    print_separator("TEST 6: Filter Components - GPUs")
    
    params = {
        "component_type": "GPU",
        "max_price": 1500,
        "limit": 5
    }
    
    response = requests.get(f"{BASE_URL}/components", params=params)
    data = response.json()
    
    print(f"✓ Status Code: {response.status_code}")
    print(f"\nFiltros aplicados:")
    print(f"  Tipo: {params['component_type']}")
    print(f"  Precio máximo: S/ {params['max_price']:,}")
    print(f"  Límite: {params['limit']}")
    
    print(f"\n📦 Resultados ({data['count']} encontrados):")
    for comp in data['components'][:5]:
        print(f"  {comp['name'][:50]:50s} S/ {comp['regular_price']:7,.0f}")
    
    assert response.status_code == 200
    assert data['count'] > 0
    print("\n✅ Test 6 PASSED")

def test_7_component_types():
    """Test: Listar tipos de componentes"""
    print_separator("TEST 7: Component Types")
    
    response = requests.get(f"{BASE_URL}/components/types")
    data = response.json()
    
    print(f"✓ Status Code: {response.status_code}")
    print(f"\nTipos de componentes disponibles:")
    
    for comp_type in sorted(data['types']):
        count = data['counts'][comp_type]
        print(f"  {comp_type:12s}: {count:3d} componentes")
    
    assert response.status_code == 200
    print("\n✅ Test 7 PASSED")

def test_8_validate_config():
    """Test: Validar compatibilidad"""
    print_separator("TEST 8: Validate Configuration")
    
    # Configuración de prueba (compatible)
    payload = {
        "components": {
            "CPU": {
                "features": {
                    "socket": "Socket AM4",
                    "tdp_watts": 65
                }
            },
            "MOTHERBOARD": {
                "features": {
                    "socket": "Socket AM4",
                    "supported_ram_type": "DDR4"
                }
            },
            "RAM": {
                "features": {
                    "ram_type": "DDR4"
                }
            },
            "PSU": {
                "features": {
                    "wattage": 500
                }
            }
        }
    }
    
    response = requests.post(f"{BASE_URL}/validate", json=payload)
    data = response.json()
    
    print(f"✓ Status Code: {response.status_code}")
    print(f"\nResultado de validación:")
    print(f"  ✓ Compatible: {data['is_valid']}")
    print(f"  ✓ Errores: {len(data['errors'])}")
    print(f"  ✓ Advertencias: {len(data['warnings'])}")
    
    if data['warnings']:
        print(f"\n  Advertencias:")
        for warning in data['warnings']:
            print(f"    - {warning}")
    
    assert response.status_code == 200
    print("\n✅ Test 8 PASSED")

def test_9_compare_models():
    """Test: Comparar modelos NCF vs Reglas"""
    print_separator("TEST 9: Compare Models")
    
    payload = {
        "message": "PC para diseño gráfico, 2800 soles"
    }
    
    response = requests.post(f"{BASE_URL}/compare-models", json=payload)
    data = response.json()
    
    print(f"✓ Status Code: {response.status_code}")
    print(f"\nComparación de modelos:")
    
    print(f"\n📊 Modelo NCF:")
    print(f"  Total: S/ {data['ncf']['costs']['total']:,.0f}")
    print(f"  Compatible: {data['ncf']['compatibility']['is_valid']}")
    
    print(f"\n📊 Modelo Reglas:")
    print(f"  Total: S/ {data['rules']['costs']['total']:,.0f}")
    print(f"  Compatible: {data['rules']['compatibility']['is_valid']}")
    
    assert response.status_code == 200
    assert 'ncf' in data
    assert 'rules' in data
    print("\n✅ Test 9 PASSED")

def test_10_recommend_by_profile():
    """Test: Recomendar componente específico"""
    print_separator("TEST 10: Recommend by Profile")
    
    profile_id = "gamer_mid"
    component_type = "GPU"
    
    response = requests.get(
        f"{BASE_URL}/recommend/{profile_id}/{component_type}",
        params={"model_type": "rule", "top_k": 3}
    )
    data = response.json()
    
    print(f"✓ Status Code: {response.status_code}")
    print(f"\nPerfil: {profile_id}")
    print(f"Componente: {component_type}")
    print(f"Modelo: {data['model_used']}")
    
    print(f"\n🎯 Top {len(data['recommendations'])} recomendaciones:")
    for i, rec in enumerate(data['recommendations'], 1):
        print(f"  {i}. {rec['name'][:45]:45s} S/ {rec['price']:7,.0f} | Rating: {rec['predicted_rating']:.2f}")
    
    assert response.status_code == 200
    print("\n✅ Test 10 PASSED")

def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "="*70)
    print("  🧪 SUITE COMPLETA DE PRUEBAS DE LA API")
    print("="*70)
    
    tests = [
        test_1_health,
        test_2_chat_gamer,
        test_3_chat_developer,
        test_4_recommend_gamer,
        test_5_profiles,
        test_6_components_gpu,
        test_7_component_types,
        test_8_validate_config,
        test_9_compare_models,
        test_10_recommend_by_profile
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"\n❌ Test FAILED: {e}")
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Error de conexión")
            print("   Asegúrate que la API esté corriendo en http://localhost:8000")
            return
        except Exception as e:
            failed += 1
            print(f"\n❌ Error inesperado: {e}")
    
    print("\n" + "="*70)
    print(f"  📊 RESULTADOS FINALES")
    print("="*70)
    print(f"  ✅ Tests pasados: {passed}")
    print(f"  ❌ Tests fallidos: {failed}")
    print(f"  📈 Tasa de éxito: {passed/(passed+failed)*100:.1f}%")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_all_tests()