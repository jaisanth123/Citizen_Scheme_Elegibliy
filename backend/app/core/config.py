import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "app" / "data"
EXPORTS_DIR = BASE_DIR / "exports"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    APP_NAME: str = "Veritas Misinformation Fact-Checking Pipeline"
    API_V1_PREFIX: str = "/api"
    ENV: str = "development"
    
    # Tavily Web Search API
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    
    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto") # "ollama", "openai", "gemini", "mock", "auto"
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Database
    DATABASE_PATH: Path = BASE_DIR / "data" / "factcheck.db"
    
    # Multi-Agent Parameters
    MAX_CRITIC_ROUNDS: int = 2
    CONFIDENCE_THRESHOLD: float = 0.65
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
# Ensure data dir exists
settings.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
