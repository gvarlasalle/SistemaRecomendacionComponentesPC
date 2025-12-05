# backend/data_layer/test_scraper_debug.py
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def test_pcfactory_scraping():
    """Prueba de debugging para ver qué está pasando"""
    
    print("\n" + "="*60)
    print("🔍 TEST DE DEBUGGING - PCFactory Scraper")
    print("="*60)
    
    # Configurar Chrome
    chrome_options = Options()
    # IMPORTANTE: Quitar --headless para VER qué pasa
    # chrome_options.add_argument('--headless')  # <-- COMENTADO
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        url = 'https://www.pcfactory.com.pe/memorias?categoria=264'
        
        print(f"\n📡 Accediendo a: {url}")
        driver.get(url)
        
        print("⏳ Esperando 5 segundos para que cargue completamente...")
        time.sleep(5)
        
        # Crear carpeta debug dentro de data_layer
        current_dir = os.path.dirname(os.path.abspath(__file__))
        debug_dir = os.path.join(current_dir, 'debug')
        os.makedirs(debug_dir, exist_ok=True)
        
        # Guardar screenshot
        screenshot_path = os.path.join(debug_dir, 'screenshot.png')
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot guardado: {screenshot_path}")
        
        # Guardar HTML
        html_path = os.path.join(debug_dir, 'page_source.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"📄 HTML guardado: {html_path}")
        
        # Intentar encontrar productos
        print("\n🔍 Buscando productos...")
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Método 1: Buscar por clase 'product'
        products_div = soup.find_all('div', class_='product')
        print(f"   Método 1 (class='product'): {len(products_div)} productos")
        
        # Método 2: Buscar por atributo data-class
        products_data = soup.find_all('div', attrs={'data-class': 'Caluga'})
        print(f"   Método 2 (data-class='Caluga'): {len(products_data)} productos")
        
        # Método 3: Buscar por clase product-list
        product_list = soup.find('div', class_='product-list')
        if product_list:
            products_in_list = product_list.find_all('div', class_='product')
            print(f"   Método 3 (dentro de product-list): {len(products_in_list)} productos")
        else:
            print("   Método 3: No se encontró div.product-list")
        
        # Mostrar los primeros 3 productos encontrados (si hay)
        if products_div:
            print("\n📦 Primeros 3 productos encontrados:")
            for i, product in enumerate(products_div[:3], 1):
                try:
                    # Buscar nombre
                    name_elem = product.find('div', class_='product__card-title')
                    name = name_elem.text.strip() if name_elem else "No encontrado"
                    
                    # Buscar precio
                    price_elem = product.find('div', class_='title-md color-primary-1')
                    price = price_elem.text.strip() if price_elem else "No encontrado"
                    
                    print(f"\n   Producto {i}:")
                    print(f"   - Nombre: {name[:50]}...")
                    print(f"   - Precio: {price}")
                    
                except Exception as e:
                    print(f"   - Error extrayendo producto {i}: {e}")
        else:
            print("\n❌ NO se encontraron productos")
            print("\n🔍 Verificando estructura de la página...")
            
            # Verificar si hay algún mensaje de error o página diferente
            title = soup.find('title')
            print(f"   Título de página: {title.text if title else 'No encontrado'}")
            
            # Buscar si hay mensaje de "sin productos"
            no_products = soup.find('div', id='msg_sin_productos')
            if no_products:
                print("   ⚠️  Página muestra mensaje 'sin productos'")
        
        print("\n✅ Debugging completado")
        print(f"   Revisa los archivos en: {debug_dir}")
        print(f"   - Screenshot: screenshot.png")
        print(f"   - HTML: page_source.html")
        
        input("\n👉 Presiona ENTER para cerrar el navegador...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        driver.quit()
        print("\n🔒 Navegador cerrado")

if __name__ == "__main__":
    test_pcfactory_scraping()