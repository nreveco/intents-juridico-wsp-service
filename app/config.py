from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Ollama (LLM local)
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

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
