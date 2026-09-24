"""Runtime settings read from environment variables (.env). Owner: P3."""
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me")
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    dev_auth: bool = os.getenv("DEV_AUTH", "false").lower() == "true"
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "")
    llm_timeout_s: float = float(os.getenv("LLM_TIMEOUT_S", "20"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./storage/app.db")
    chroma_dir: str = os.getenv("CHROMA_DIR", "./storage/chroma")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
    rag_min_score: float = float(os.getenv("RAG_MIN_SCORE", "0.35"))
    use_local_intent: bool = os.getenv("USE_LOCAL_INTENT", "false").lower() == "true"


settings = Settings()
