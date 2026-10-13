"""Configuration settings."""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # GCP Configuration
    GCP_PROJECT_ID: Optional[str] = os.getenv("GCP_PROJECT_ID")
    GCP_REGION: str = os.getenv("GCP_REGION", "us-central1")
    FIRESTORE_DATABASE: str = os.getenv("FIRESTORE_DATABASE", "default")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Agent Configuration
    MAX_RETRIES: int = 3
    TIMEOUT_SECONDS: int = 30
    
    # Knowledge Base Configuration
    KNOWLEDGE_BASE_ENABLED: bool = os.getenv("KNOWLEDGE_BASE_ENABLED", "true").lower() == "true"
    
    # Speech Configuration
    SPEECH_LANGUAGE_CODE: str = os.getenv("SPEECH_LANGUAGE_CODE", "en-US")
    SPEECH_SAMPLE_RATE: int = int(os.getenv("SPEECH_SAMPLE_RATE", "16000"))
    TTS_VOICE_NAME: str = os.getenv("TTS_VOICE_NAME", "en-US-Neural2-D")
    TTS_VOICE_GENDER: str = os.getenv("TTS_VOICE_GENDER", "NEUTRAL")
    ENABLE_STT_TTS: bool = os.getenv("ENABLE_STT_TTS", "true").lower() == "true"


config = Config()

