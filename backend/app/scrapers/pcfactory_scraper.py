import re
from typing import List, Dict, Optional
from app.scrapers.base_scraper import BaseScraper
from app.models.components import ComponentType, StoreSource
from app.utils.logger import get_logger
from bs4 import BeautifulSoup

logger = get_logger(__name__)


class PCFactoryScraper(BaseScraper):
    """Scraper para PC Factory Perú"""
    
    def __init__(self):
        super().__init__(StoreSource.PCFACTORY)
        
        self.category_urls = {
            ComponentType.PROCESSOR: "https://www.pcfactory.com.pe/componentes-partes-y-piezas/procesadores?categoria=272&papa=633",
            ComponentType.MOTHERBOARD: "https://www.pcfactory.com.pe/placas-madres?categoria=292",
            ComponentType.RAM: "https://www.pcfactory.com.pe/memorias?categoria=264",
            ComponentType.GPU: "https://www.pcfactory.com.pe/componentes-partes-y-piezas/tarjetas-graficas?categoria=334&papa=633",
            ComponentType.STORAGE: "https://www.pcfactory.com.pe/componentes-partes-y-piezas/almacenamiento?categoria=312&papa=633",
            ComponentType.PSU: "https://www.pcfactory.com.pe/componentes-partes-y-piezas/fuentes-de-poder-psu-?categoria=54&papa=633",
            ComponentType.CASE: "https://www.pcfactory.com.pe/componentes-partes-y-piezas/gabinetes?categoria=326&papa=633",
        }
    
    async def scrape_category(self, component_type: ComponentType) -> List[Dict]:
        """Scrape una categoría de PC Factory"""
        url = self.category_urls.get(component_type)
        if not url:
            logger.warning(f"No URL for {component_type}")
            return []
        
        logger.info(f"Scraping {component_type.value} from PC Factory...")
        products = []
        page = 1
        max_pages = 10
        
        while page <= max_pages:
            page_url = f"{url}&page={page}" if page > 1 else url
            logger.info(f"Fetching page {page}")
            
            html = await self._fetch_url(page_url)
            if not html:
                break
            
            soup = BeautifulSoup(html, "lxml")
            product_elements = soup.select(".product-list .product")
            
            if not product_elements:
                logger.info(f"No more products on page {page}")
                break
            
            logger.info(f"Found {len(product_elements)} products")
            
            for element in product_elements:
                product_data = self._extract_product_data(element, component_type)
                if product_data:
                    products.append(product_data)
            
            self._random_delay()
            page += 1
        
        logger.info(f"Total scraped: {len(products)} products")
        return products
    
    def _extract_product_data(self, element, component_type: ComponentType) -> Optional[Dict]:
        """Extrae datos de un producto"""
        try:
            product_id = element.get("id", "").replace("caluga_", "")
            if not product_id:
                return None
            
            # Marca
            brand_elem = element.select_one(".product__heading .card-title")
            brand = brand_elem.get_text(strip=True).replace("®", "").strip() if brand_elem else "Unknown"
            
            # Nombre
            name_elem = element.select_one(".product__card-title")
            name = name_elem.get_text(strip=True) if name_elem else None
            
            if not name:
                return None
            
            # Filtro para RAM
            if component_type == ComponentType.RAM:
                name_lower = name.lower()
                exclude_keywords = ["usb", "pendrive", "flash", "micro sd"]
                if any(kw in name_lower for kw in exclude_keywords):
                    return None
                ram_keywords = ["ddr", "dimm", "ram"]
                if not any(kw in name_lower for kw in ram_keywords):
                    return None
            
            # Precio
            price_elem = element.select_one(".title-md.color-primary-1 span:last-child")
            price = self._clean_price(price_elem.get_text(strip=True)) if price_elem else None
            
            # Stock
            stock_elem = element.select_one(".product__units .link--sm")
            stock_text = stock_elem.get_text(strip=True) if stock_elem else "0 Unid."
            stock_match = re.search(r"(\d+)", stock_text)
            stock_quantity = int(stock_match.group(1)) if stock_match else 0
            
            # Imagen
            img_elem = element.select_one(".product__image img")
            image_url = img_elem.get("src") if img_elem else None
            
            # URL producto
            link_elem = element.select_one(".product-ab-link")
            product_url = f"https://www.pcfactory.com.pe{link_elem.get('href')}" if link_elem and link_elem.get("href") else None
            
            # Especificaciones
            specifications = self._parse_specifications(name, component_type)
            
            return {
                "name": name,
                "brand": brand,
                "component_type": component_type,
                "price": price or 0.0,
                "in_stock": stock_quantity > 0,
                "store_source": self.store_source,
                "product_url": product_url,
                "image_url": image_url,
                "specifications": specifications,
            }
        
        except Exception as e:
            logger.error(f"Error extracting product: {e}")
            return None
    
    def _parse_specifications(self, name: str, component_type: ComponentType) -> Dict:
        """Parsea especificaciones del nombre"""
        specs = {}
        name_lower = name.lower()
        
        if component_type == ComponentType.PROCESSOR:
            # Núcleos
            cores_match = re.search(r"(\d+)\s*n[uú]cleos?", name_lower)
            if cores_match:
                specs["cores"] = int(cores_match.group(1))
            
            # Frecuencia
            freq_match = re.search(r"(\d+\.?\d*)\s*ghz", name_lower)
            if freq_match:
                specs["base_frequency"] = f"{freq_match.group(1)} GHz"
            
            # Socket
            if "am4" in name_lower:
                specs["socket"] = "AM4"
            elif "am5" in name_lower:
                specs["socket"] = "AM5"
            elif "lga1700" in name_lower:
                specs["socket"] = "LGA1700"
        
        elif component_type == ComponentType.RAM:
            # Capacidad
            capacity_match = re.search(r"(\d+)\s*gb", name_lower)
            if capacity_match:
                specs["capacity"] = f"{capacity_match.group(1)}GB"
            
            # Velocidad
            speed_match = re.search(r"(\d{4,5})\s*mhz", name_lower)
            if speed_match:
                specs["speed"] = f"{speed_match.group(1)} MHz"
            
            # Tipo DDR
            if "ddr5" in name_lower:
                specs["type"] = "DDR5"
            elif "ddr4" in name_lower:
                specs["type"] = "DDR4"
        
        elif component_type == ComponentType.GPU:
            # VRAM
            vram_match = re.search(r"(\d+)\s*gb", name_lower)
            if vram_match:
                specs["vram"] = f"{vram_match.group(1)}GB"
        
        elif component_type == ComponentType.STORAGE:
            # Capacidad
            capacity_patterns = [
                (r"(\d+)\s*tb", "TB"),
                (r"(\d+)\s*gb", "GB")
            ]
            for pattern, unit in capacity_patterns:
                match = re.search(pattern, name_lower)
                if match:
                    specs["capacity"] = f"{match.group(1)}{unit}"
                    break
            
            # Tipo
            if "nvme" in name_lower or "m.2" in name_lower:
                specs["type"] = "NVMe SSD"
            elif "ssd" in name_lower:
                specs["type"] = "SATA SSD"
            elif "hdd" in name_lower:
                specs["type"] = "HDD"
        
        return specs


# Instancia singleton
pcfactory_scraper = PCFactoryScraper()