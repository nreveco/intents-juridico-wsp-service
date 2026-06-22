from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # Ollama (LLM local o servidor externo)
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "qwen2.5:7b"
    ollama_vision_model: str = "llava:7b"

    # Meta Cloud API
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_verify_token: str = "default_verify_token"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/automation_db"

    # Admin API Key
    admin_api_key: str = "change_me_in_production"

    # App
    debug: bool = False
    environment: str = "development"
    port: int = 8000

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def is_production(self) -> bool:
        """Detecta si está corriendo en Railway"""
        return self.environment == "production" or os.getenv("RAILWAY_ENVIRONMENT") is not None


settings = Settings()
