from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Dataset & Storage
    csv_path: str = Field(
        default=str(BASE_DIR / "data" / "smartphones_data.csv.csv"),
        alias="CSV_PATH"
    )
    sqlite_db_path: str = Field(
        default=str(BASE_DIR / "data" / "smartphones.db"),
        alias="SQLITE_DB_PATH"
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        alias="REDIS_URL"
    )
    
    # OpenRouter LLM Configuration
    open_router_api: str = Field(
        default="",
        alias="OPEN_ROUTER_API"
    )
    open_router_base_url: str = "https://openrouter.ai/api/v1"
    open_router_model: str = Field(
        default="google/gemma-4-26b-a4b-it:free",
        alias="OPEN_ROUTER_MODEL"
    )
    fallback_models: list = [
        "google/gemma-4-26b-a4b-it:free",
        "liquid/lfm-3-1.7b:free",
        "nvidia/nemotron-3.5-lightning:free",
    ]
    
    # Rate Limits (OpenRouter free model tier: 20 req/min, 1000 req/day)
    llm_rpm_limit: int = 20
    llm_rpd_limit: int = 1000
    virtual_llm_mode: bool = Field(
        default=False,
        alias="VIRTUAL_LLM_MODE"
    )
    
    # Caching & Optimization Thresholds
    exact_cache_ttl_seconds: int = 3600      # 1 hour
    semantic_cache_ttl_seconds: int = 7200   # 2 hours
    search_cache_ttl_seconds: int = 600      # 10 minutes
    semantic_similarity_threshold: float = 0.88
    
    # Baseline Cost Assumptions (Per 1 Million Tokens in USD, benchmarked to standard production models)
    cost_per_million_input_tokens_usd: float = 2.50
    cost_per_million_output_tokens_usd: float = 10.00
    usd_to_inr_rate: float = 86.50

    model_config = {
        "env_file": str(BASE_DIR / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "populate_by_name": True,
    }

settings = Settings()
