from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import httpx
import random
import time
from bs4 import BeautifulSoup
from app.config import settings
from app.utils.logger import get_logger
from app.models.components import ComponentType, StoreSource

logger = get_logger(__name__)


class BaseScraper(ABC):
    """Clase base para scrapers"""
    
    def __init__(self, store_source: StoreSource):
        self.store_source = store_source
        self.max_retries = 3
        self.timeout = 30
        self.headers = {
            "User-Agent": settings.SCRAPER_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "es-ES,es;q=0.9",
        }
    
    def _random_delay(self):
        """Delay aleatorio entre requests"""
        time.sleep(random.uniform(1, 3))
    
    async def _fetch_url(self, url: str) -> Optional[str]:
        """Fetch URL con reintentos"""
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        url,
                        headers=self.headers,
                        timeout=self.timeout,
                        follow_redirects=True
                    )
                    response.raise_for_status()
                    logger.info(f"Fetched: {url}")
                    return response.text
            except Exception as e:
                if attempt < self.max_retries - 1:
                    self._random_delay()
                else:
                    logger.error(f"Failed to fetch {url}: {e}")
                    return None
        return None
    
    def _clean_price(self, price_text: str) -> Optional[float]:
        """Limpia texto de precio"""
        try:
            cleaned = price_text.replace("S/", "").replace(",", "").strip()
            return float(cleaned)
        except:
            return None
    
    @abstractmethod
    async def scrape_category(self, component_type: ComponentType) -> List[Dict]:
        """Método a implementar por scrapers específicos"""
        pass