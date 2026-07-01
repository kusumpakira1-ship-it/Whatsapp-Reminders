import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str = os.getenv("DB_HOST", "145.223.17.70")
    DB_NAME: str = os.getenv("DB_NAME", "u632391467_yaswanth")
    DB_USER: str = os.getenv("DB_USER", "u632391467_yaswanth")
    DB_PASS: str = os.getenv("DB_PASS", "Yaswanth@2026Cc!")
    WAHA_URL: str = os.getenv("WAHA_URL", "http://waha:3000")
    WAHA_SESSION: str = os.getenv("WAHA_SESSION", "default")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini")
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    OLLAMA_VISION_MODEL: str = os.getenv("OLLAMA_VISION_MODEL", "llava")
    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")

settings = Settings()
