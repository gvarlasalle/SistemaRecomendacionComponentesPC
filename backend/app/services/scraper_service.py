from typing import List, Dict
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.components import Component, ComponentType, StoreSource
from app.scrapers.pcfactory_scraper import pcfactory_scraper
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ScraperService:
    """Servicio para gestionar scraping y almacenamiento"""
    
    def __init__(self, db: Session):
        self.db = db
        self.scrapers = {
            StoreSource.PCFACTORY: pcfactory_scraper,
        }
    
    async def scrape_and_store(self, store_source: StoreSource, component_type: ComponentType):
        """Ejecuta scraping y almacena datos"""
        logger.info(f"Starting scraper for {store_source.value} - {component_type.value}")
        
        try:
            scraper = self.scrapers.get(store_source)
            if not scraper:
                raise ValueError(f"No scraper for {store_source}")
            
            products = await scraper.scrape_category(component_type)
            logger.info(f"Scraped {len(products)} products")
            
            successful = 0
            failed = 0
            
            for product_data in products:
                try:
                    self._store_component(product_data)
                    successful += 1
                except Exception as e:
                    logger.error(f"Error storing product: {e}")
                    failed += 1
            
            logger.info(f"Completed: {successful} inserted, {failed} failed")
            return {"successful": successful, "failed": failed}
            
        except Exception as e:
            logger.error(f"Scraper failed: {e}")
            raise
    
    def _store_component(self, product_data: Dict):
        """Almacena un componente"""
        component = Component(**product_data)
        self.db.add(component)
        self.db.commit()
        logger.debug(f"Stored: {component.name}")
    
    async def scrape_all_categories(self, store_source: StoreSource):
        """Scrapea todas las categorías"""
        results = []
        for component_type in ComponentType:
            try:
                result = await self.scrape_and_store(store_source, component_type)
                results.append(result)
            except Exception as e:
                logger.error(f"Error scraping {component_type.value}: {e}")
        return results