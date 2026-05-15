from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Config
    PROJECT_NAME: str = "Advanced Asynchronous Backend System"
    VERSION: str = "1.4.2-Prod"
    
    # Security
    SECRET_KEY_ACCESS: str
    SECRET_KEY_REFRESH: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    DATABASE_URL: Optional[str] = None

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # Default to SQLite for easy development if Postgres info is incomplete
        if not self.POSTGRES_USER or not self.POSTGRES_PASSWORD:
            return "sqlite+aiosqlite:///./sql_app.db"
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
