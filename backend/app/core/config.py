from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # General
    APP_NAME: str = "TradeTrace"
    APP_VERSION: str = "0.1.0"
    TAGLINE: str = "Research -> Challenge -> Decide -> Monitor -> Trace -> Learn"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    DEMO_MODE: bool = True
    API_V1_STR: str = "/api/v1"

    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, str) and v.startswith("["):
            import json
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
        return v if isinstance(v, list) else ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Security & Auth
    JWT_SECRET: str = "tradetrace-super-secure-dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/tradetrace"
    DATABASE_SYNC_URL: str = "postgresql://postgres:postgres@localhost:5432/tradetrace"

    # LLM Provider Configuration
    LLM_PROVIDER: str = "mock"  # "mock" | "openai" | "anthropic" | "gemini"
    LLM_API_KEY: str = "mock-key"
    LLM_MODEL: str = "mock-trading-intelligence-v1"
    LLM_BASE_URL: str = ""
    LLM_TEMPERATURE: float = 0.2

    # Market Data Provider Configuration
    MARKET_DATA_PROVIDER: str = "mock"  # "mock" | "polygon" | "alphavantage" | "yfinance"
    MARKET_DATA_API_KEY: str = "mock-key"

    # Financial News Provider Configuration
    NEWS_PROVIDER: str = "mock"  # "mock" | "finnhub" | "newsapi"
    NEWS_API_KEY: str = "mock-key"

    # Paper Trading Defaults
    INITIAL_PAPER_BALANCE: float = 100000.0
    DEFAULT_RISK_PER_TRADE_PCT: float = 1.0
    MAX_PORTFOLIO_EXPOSURE_PCT: float = 50.0

    # Monitoring Worker
    MONITORING_INTERVAL_SECONDS: int = 60


settings = Settings()
