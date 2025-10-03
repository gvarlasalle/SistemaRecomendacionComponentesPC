"""
Script para ejecutar scraping manual
Uso: python -m backend.scripts.manual_scrape
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database import SessionLocal, init_db
from app.services.scraper_service import ScraperService
from app.models.components import StoreSource
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def main():
    logger.info("=" * 80)
    logger.info("SCRAPING MANUAL - PC FACTORY")
    logger.info("=" * 80)
    
    init_db()
    db = SessionLocal()
    
    try:
        scraper_service = ScraperService(db)
        logger.info("Iniciando scraping de todas las categorías...")
        
        results = await scraper_service.scrape_all_categories(StoreSource.PCFACTORY)
        
        total_success = sum(r["successful"] for r in results)
        total_failed = sum(r["failed"] for r in results)
        
        logger.info("=" * 80)
        logger.info(f"COMPLETADO: {total_success} exitosos, {total_failed} fallidos")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())