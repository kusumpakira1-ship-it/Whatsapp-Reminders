import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str = os.getenv("DB_HOST", "145.223.17.70")
    DB_NAME: str = os.getenv("DB_NAME", "u632391467_yaswanth")
    DB_USER: str = os.getenv("DB_USER", "u632391467_yaswanth")
    DB_PASS: str = os.getenv("DB_PASS", "Yaswanth@2026Cc!")
    MANAGER_PHONE: str = os.getenv("MANAGER_PHONE", "917975209680")
    WAHA_URL: str = os.getenv("WAHA_URL", "http://waha:3000")
    WAHA_SESSION: str = os.getenv("WAHA_SESSION", "default")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini")
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    OLLAMA_VISION_MODEL: str = os.getenv("OLLAMA_VISION_MODEL", "llava")
    USE_N8N: str = os.getenv("USE_N8N", "false")
    ZOHO_CLIENT_ID: str = os.getenv("ZOHO_CLIENT_ID", "1000.4NB8AJUGTTJY1MIBKIA2X5O1E70N2S")
    ZOHO_CLIENT_SECRET: str = os.getenv("ZOHO_CLIENT_SECRET", "112554efa1b33cec9a81eefbaa7b411c9eb980b6b1")
    ZOHO_DOMAIN: str = os.getenv("ZOHO_DOMAIN", "zoho.com")
    ZOHO_RECIPIENT_PHONE: str = os.getenv("ZOHO_RECIPIENT_PHONE", "917259510983")
    ZOHO_REDIRECT_URI: str = os.getenv("ZOHO_REDIRECT_URI", "https://sunfragroup.com/kusum/Whatsapp_Rem/callback.php")
    class Config:
        extra = 'ignore'
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

settings = Settings()

