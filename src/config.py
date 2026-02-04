"""
FastAPI Application Configuration

환경변수 기반 설정 관리
"""
from functools import lru_cache
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    app_name: str = "FastAPI Backend"
    debug: bool = False
    secret_key: str = "your-secret-key-here-change-in-production"
    api_v1_prefix: str = "/api"
    
    # Database
    db_engine: str = "postgresql"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "fastapi_db"
    db_user: str = "postgres"
    db_password: str = ""
    
    # JWT Settings
    jwt_secret_key: str = "your-jwt-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 5
    jwt_refresh_token_expire_days: int = 1
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "https://hrletsgo.me"]
    
    # API Keys
    openai_api_key: str = ""
    google_api_key: str = ""
    deepl_api_key: str = ""
    
    # File Storage
    media_root: str = "./media"
    static_root: str = "./static"
    blog_post_path: str = "./data/blog_posts"
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v
    
    @property
    def database_url(self) -> str:
        """동기 데이터베이스 URL 생성"""
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
    
    @property
    def async_database_url(self) -> str:
        """비동기 데이터베이스 URL 생성 (asyncpg)"""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글턴 반환"""
    return Settings()


settings = get_settings()
