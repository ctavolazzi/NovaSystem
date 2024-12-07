from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str

    # Database
    database_url: str = "sqlite+aiosqlite:///./nova.db"

    # LLM Settings
    ollama_host: str = "http://localhost:11434"
    default_model: str = "gpt-4"
    default_temperature: float = 0.7

    # Application Settings
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()