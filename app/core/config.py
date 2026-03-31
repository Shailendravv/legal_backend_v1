from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GROQ_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    ADMIN_API_KEY: str
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

