# filepath: backend/app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Explainable Chess AI API"
    debug: bool = True
    # Add more config variables as needed

settings = Settings()