import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.routes.fact_check_routes import router as fact_check_router
from app.routes.digest_routes import router as digest_router
from app.routes.archive_routes import router as archive_router
from app.routes.eval_routes import router as eval_router
from app.routes.health_routes import router as health_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("factcheck.app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database and seeding datasets...")
    init_db()
    logger.info(f"{settings.APP_NAME} started successfully.")
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-Agent Fact-Checking and Misinformation Detection Pipeline with LangGraph, MCP, and Tavily Search.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers under API prefix
app.include_router(fact_check_router, prefix=settings.API_V1_PREFIX)
app.include_router(digest_router, prefix=settings.API_V1_PREFIX)
app.include_router(archive_router, prefix=settings.API_V1_PREFIX)
app.include_router(eval_router, prefix=settings.API_V1_PREFIX)
app.include_router(health_router, prefix=settings.API_V1_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
