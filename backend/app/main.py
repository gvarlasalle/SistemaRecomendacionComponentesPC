from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db
from app.api.routes import health, components
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando API...")
    try:
        init_db()
        logger.info("BD inicializada")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    yield
    logger.info("API detenida")


app = FastAPI(
    title="PC Components Recommendation System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(components.router, prefix="/api/v1", tags=["Components"])


@app.get("/")
def root():
    return {
        "message": "PC Recommendation System API",
        "version": "1.0.0",
        "docs": "/docs"
    }