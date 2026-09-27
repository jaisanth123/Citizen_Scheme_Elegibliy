import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.core.config import settings
from app.services.tavily_service import tavily_service
from app.core.database import get_db_connection

router = APIRouter(prefix="", tags=["System"])

class ConfigUpdate(BaseModel):
    tavily_api_key: Optional[str] = None
    llm_provider: Optional[str] = None
    openai_api_key: Optional[str] = None

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "env": settings.ENV
    }

@router.get("/config")
def get_config_status():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM saved_claims")
    claims_count = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(*) as cnt FROM saved_digests")
    digests_count = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(*) as cnt FROM trusted_sources")
    sources_count = cursor.fetchone()["cnt"]
    conn.close()

    return {
        "tavily_configured": tavily_service.is_configured(),
        "llm_provider": settings.LLM_PROVIDER,
        "ollama_model": settings.OLLAMA_MODEL,
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "database_stats": {
            "total_claims": claims_count,
            "total_digests": digests_count,
            "trusted_sources": sources_count
        }
    }

@router.post("/config")
def update_config(update: ConfigUpdate):
    if update.tavily_api_key is not None:
        tavily_service.set_api_key(update.tavily_api_key.strip())
    if update.llm_provider:
        settings.LLM_PROVIDER = update.llm_provider.strip()
    if update.openai_api_key is not None:
        settings.OPENAI_API_KEY = update.openai_api_key.strip()

    return {"status": "success", "message": "Configuration updated successfully."}
