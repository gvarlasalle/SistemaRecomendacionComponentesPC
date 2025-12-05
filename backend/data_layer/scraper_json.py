# backend/data_layer/scraper_json.py
import time
import os
import re
import random
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from typing import List, Dict
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

class PCFactoryScraperJSON:
    """
    Web scraper que guarda directamente en JSON
    Perfecto para datasets académicos/tesis
    """
    
    CATEGORIES = {
        'procesadores': {
            'url': 'https://www.pcfactory.com.pe/procesadores?categoria=272',
            'type': 'CPU'
        },
        'tarjetas-graficas': {
            'url': 'https://www.pcfactory.com.pe/tarjetas-graficas?categoria=334',
            'type': 'GPU'
        },
        'memorias': {
            'url': 'https://www.pcfactory.com.pe/memorias-pc?categoria=112',  # ← CORREGIDO
            'type': 'RAM'
        },
        'placas-madre': {
            'url': 'https://www.pcfactory.com.pe/placas-madres?categoria=292',  # ← CORREGIDO
            'type': 'MOTHERBOARD'
        },
        'almacenamiento': {
            'url': 'https://www.pcfactory.com.pe/discos-ssd?categoria=585',  # ← CORREGIDO
            'type': 'STORAGE'
        },
        'fuentes-de-poder': {
            'url': 'https://www.pcfactory.com.pe/fuentes-de-poder-psu-?categoria=54',
            'type': 'PSU'
        },
        'gabinetes': {
            'url': 'https://www.pcfactory.com.pe/gabinetes?categoria=326',
            'type': 'CASE'
        },
        'monitores': {  # ← NUEVO
            'url': 'https://www.pcfactory.com.pe/monitores-y-proyectores/monitores?categoria=995&papa=256',
            'type': 'MONITOR'
        }
    }
    
    def __init__(self, output_dir: str = None):
        self.base_url = 'https://www.pcfactory.com.pe'
        self.min_delay = float(os.getenv('SCRAPE_DELAY', 2))
        self.max_delay = self.min_delay * 2
        self.driver = None
        self.requests_count = 0
        self.max_requests_per_batch = 10
        
        # Directorio para guardar JSONs (DENTRO de data_layer/data)
        if output_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.output_dir = os.path.join(current_dir, 'data')
        else:
            self.output_dir = output_dir
            
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"📁 Directorio de datos: {self.output_dir}")
        
    def random_delay(self, min_delay: float = None, max_delay: float = None):
        """Pausa con tiempo randomizado"""
        min_d = min_delay or self.min_delay
        max_d = max_delay or self.max_delay
        delay = random.uniform(min_d, max_d)
        time.sleep(delay)
        
        self.requests_count += 1
        if self.requests_count % self.max_requests_per_batch == 0:
            long_pause = random.uniform(5, 10)
            print(f"⏸️  Pausa larga de {long_pause:.1f}s...")
            time.sleep(long_pause)
        
    def setup_driver(self):
        """Configura el driver de Selenium"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'user-agent={os.getenv("USER_AGENT")}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Driver configurado")
        
    def extract_price(self, price_text: str) -> float:
        """Extrae precio numérico"""
        if not price_text:
            return 0.0
        price = re.sub(r'[^\d.,]', '', price_text)
        price = price.replace(',', '')
        try:
            return float(price)
        except:
            return 0.0
    
    def get_total_pages(self, soup: BeautifulSoup) -> int:
        """Detecta número total de páginas"""
        try:
            pagination = soup.find('div', class_='div_paginacion')
            if not pagination:
                return 1
            
            page_links = pagination.find_all('a')
            if not page_links:
                return 1
            
            max_page = 1
            for link in page_links:
                page_text = link.text.strip()
                if page_text.isdigit():
                    max_page = max(max_page, int(page_text))
            
            return max_page
        except:
            return 1
    
    def scrape_product_list_page(self, url: str, comp_type: str) -> List[Dict]:
        """Extrae productos de UNA página"""
        products = []
        
        try:
            self.driver.get(url)
            self.random_delay()
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product"))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            product_cards = soup.find_all('div', class_='product')
            
            for card in product_cards:
                try:
                    id_elem = card.find('span')
                    if not id_elem:
                        continue
                    product_id = id_elem.text.strip()
                    
                    name_elem = card.find('div', class_='product__card-title')
                    if not name_elem:
                        continue
                    name = name_elem.text.strip()

                    # FILTRO: Excluir memorias flash/SD
                    if comp_type == 'RAM':
                        if any(keyword in name.lower() for keyword in ['memoria flash', 'sdxc', 'microsd', 'sd card']):
                            continue  # Saltar este producto
                    
                    brand_elem = card.find('div', class_='card-title')
                    brand = brand_elem.text.strip().replace('®', '').strip() if brand_elem else 'Sin marca'
                    
                    # PRECIO CORREGIDO - Buscar dentro del span
                    price_elem = card.find('div', class_='title-md color-primary-1 alineado-porcentaje-precio')
                    if not price_elem:
                        price_elem = card.find('div', class_='title-md color-primary-1')
                    
                    if not price_elem:
                        continue
                    
                    # Buscar el span dentro del div
                    price_span = price_elem.find('span')
                    if price_span:
                        price = self.extract_price(price_span.text)
                    else:
                        price = self.extract_price(price_elem.text)
                    
                    # Precio regular (tachado)
                    regular_price_elem = card.find('div', class_='title-sm color-gray-2 texto-tachado')
                    if regular_price_elem:
                        regular_price_span = regular_price_elem.find('span')
                        if regular_price_span:
                            regular_price = self.extract_price(regular_price_span.text)
                        else:
                            regular_price = self.extract_price(regular_price_elem.text)
                    else:
                        regular_price = price
                    
                    url_elem = card.find('a', class_='product-ab-link')
                    product_url = self.base_url + url_elem['href'] if url_elem else ''
                    
                    img_elem = card.find('img')
                    image_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else ''
                    
                    stock_elem = card.find('p', class_='link--sm color-gray-1')
                    stock_text = stock_elem.text.strip() if stock_elem else '0'
                    
                    product_data = {
                        'id': product_id,
                        'name': name,
                        'brand': brand,
                        'price': price,
                        'regular_price': regular_price,
                        'type': comp_type,
                        'url': product_url,
                        'image_url': image_url,
                        'stock': stock_text,
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    products.append(product_data)
                    
                except Exception as e:
                    continue
            
        except TimeoutException:
            print(f"⏱️  Timeout en página")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        return products
    
    def scrape_product_list_all_pages(self, base_url: str, comp_type: str, max_pages: int = None) -> List[Dict]:
        """Extrae productos de TODAS las páginas"""
        all_products = []
        
        print(f"\n🔍 Detectando número de páginas...")
        self.driver.get(base_url)
        self.random_delay()
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        total_pages = self.get_total_pages(soup)
        
        if max_pages:
            total_pages = min(total_pages, max_pages)
        
        print(f"📄 Total de páginas: {total_pages}")
        
        for page_num in range(1, total_pages + 1):
            print(f"\n📖 Página {page_num}/{total_pages}")
            
            if '?' in base_url:
                page_url = f"{base_url}&pagina={page_num}"
            else:
                page_url = f"{base_url}?pagina={page_num}"
            
            page_products = self.scrape_product_list_page(page_url, comp_type)
            all_products.extend(page_products)
            
            print(f"✅ {len(page_products)} productos encontrados")
            
            if page_num < total_pages:
                self.random_delay(min_delay=3, max_delay=6)
        
        return all_products
    
    def scrape_product_details(self, product_url: str) -> Dict:
        """Extrae especificaciones detalladas"""
        specs = {}
        
        try:
            self.driver.get(product_url)
            self.random_delay()
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-tab='fichatecnica']"))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            ficha_tecnica = soup.find('div', attrs={'data-tab': 'fichatecnica'})
            
            if ficha_tecnica:
                spec_rows = ficha_tecnica.find_all('div', class_='table__content--two-column')
                
                for row in spec_rows:
                    divs = row.find_all('div', class_='link')
                    if len(divs) >= 2:
                        key = divs[0].text.strip()
                        value = divs[1].text.strip()
                        if key and value:
                            clean_key = key.lower().replace(' ', '_').replace('(', '').replace(')', '')
                            specs[clean_key] = value
            
        except Exception as e:
            print(f"⚠️  Error en detalles: {str(e)[:50]}")
        
        return specs
    
    def map_specs_to_compatibility(self, specs: Dict, comp_type: str) -> Dict:
        """Mapea specs a compatibilidad"""
        compatibility = {}
        
        if comp_type == 'CPU':
            compatibility['socket'] = specs.get('socket', '')
            
        elif comp_type == 'GPU':
            compatibility['pcie_slot'] = 'PCIe 4.0 x16'
            compatibility['min_psu'] = specs.get('potencia', '')
                
        elif comp_type == 'RAM':
            compatibility['ram_type'] = specs.get('tipo', '')
            
        elif comp_type == 'MOTHERBOARD':
            compatibility['socket'] = specs.get('socket', '')
            compatibility['ram_type'] = specs.get('tipo_de_memoria', '')
            compatibility['form_factor'] = specs.get('formato', '')
            
        elif comp_type == 'STORAGE':
            compatibility['interface'] = specs.get('interfaz', '')
            
        elif comp_type == 'PSU':
            wattage_str = specs.get('potencia', '0')
            try:
                wattage = int(re.search(r'\d+', wattage_str).group())
                compatibility['wattage'] = wattage
            except:
                compatibility['wattage'] = 0
            
        elif comp_type == 'CASE':
            compatibility['form_factor'] = specs.get('formato', 'ATX')
            
        return compatibility
    
    def scrape_category(self, category_key: str, max_products: int = 30, max_pages: int = None) -> List[Dict]:
        """Scrape completo de una categoría"""
        category_info = self.CATEGORIES.get(category_key)
        if not category_info:
            print(f"❌ Categoría '{category_key}' no encontrada")
            return []
        
        print(f"\n{'='*60}")
        print(f"📂 Scraping: {category_key.upper()}")
        print(f"{'='*60}")
        
        products = self.scrape_product_list_all_pages(
            category_info['url'], 
            category_info['type'],
            max_pages=max_pages
        )
        
        if not products:
            print(f"⚠️  Sin productos en {category_key}")
            return []
        
        products = products[:max_products]
        print(f"\n📊 Productos a detallar: {len(products)}")
        
        enriched_products = []
        
        for i, product in enumerate(tqdm(products, desc=f"Detalles {category_key}")):
            try:
                specs = self.scrape_product_details(product['url'])
                
                product['specs'] = specs
                product['compatibility'] = self.map_specs_to_compatibility(specs, product['type'])
                
                enriched_products.append(product)
                self.random_delay()
                
            except Exception as e:
                print(f"⚠️  Error en producto {i+1}: {e}")
                continue
        
        print(f"✅ {len(enriched_products)} productos OK")
        return enriched_products
    
    def save_to_json(self, data: List[Dict], filename: str = None):
        """Guarda datos en JSON"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"components_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Guardado en: {filepath}")
        print(f"📊 Total items: {len(data)}")
        
        # Guardar también por categoría
        by_type = {}
        for item in data:
            item_type = item['type']
            if item_type not in by_type:
                by_type[item_type] = []
            by_type[item_type].append(item)
        
        for comp_type, items in by_type.items():
            type_file = os.path.join(self.output_dir, f"{comp_type.lower()}s.json")
            with open(type_file, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            print(f"   └─ {comp_type}: {len(items)} items → {os.path.basename(type_file)}")
    
    def run(self, categories: List[str] = None, max_products_per_category: int = 20, max_pages_per_category: int = 2):
        """Ejecuta scraping y guarda en JSON"""
        print("\n" + "="*60)
        print("🚀 WEB SCRAPING → JSON")
        print("="*60)
        print(f"⏱️  Delay: {self.min_delay}s - {self.max_delay}s")
        print(f"📄 Páginas máx: {max_pages_per_category if max_pages_per_category else 'TODAS'}")
        print(f"📦 Productos máx/categoría: {max_products_per_category}")
        
        if not categories:
            categories = list(self.CATEGORIES.keys())
        
        try:
            self.setup_driver()
            
            all_products = []
            
            for category in categories:
                products = self.scrape_category(
                    category, 
                    max_products=max_products_per_category,
                    max_pages=max_pages_per_category
                )
                all_products.extend(products)
                print(f"\n📊 Total acumulado: {len(all_products)} productos")
            
            if all_products:
                self.save_to_json(all_products)
            else:
                print("\n⚠️  Sin productos para guardar")
            
            print(f"\n{'='*60}")
            print("✅ SCRAPING COMPLETADO")
            print(f"⏱️  Total requests: {self.requests_count}")
            print(f"{'='*60}\n")
            
            return all_products
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()
                print("🔒 Driver cerrado")


if __name__ == "__main__":
    scraper = PCFactoryScraperJSON()
    
    # SCRAPING COMPLETO: TODAS las categorías, TODAS las páginas
    scraper.run(
        categories=None,  # None = todas las categorías
        max_products_per_category=None,  # None = sin límite
        max_pages_per_category=None  # None = todas las páginas
    )