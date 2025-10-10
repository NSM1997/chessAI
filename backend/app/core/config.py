# filepath: backend/app/core/config.py

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # API Configuration
    app_name: str = "Explainable Chess AI API"
    debug: bool = True
    api_host: str = "localhost"
    api_port: int = 8000
    log_level: str = "INFO"
    
    # Chess Engine Configuration
    stockfish_path: str = "E:/NCI/Thesis/explainable-chess-ai/stockfish/stockfish-windows-x86-64-avx2.exe"
    stockfish_depth: int = 15
    stockfish_threads: int = 2
    stockfish_hash: int = 256
    
    # ML Configuration
    model_path: str = "backend/models/saved_models"
    cache_size: int = 1000
    enable_ml_analysis: bool = True
    
    # Data Configuration
    data_path: str = "backend/data"
    pgn_path: str = "backend/data/raw"
    processed_path: str = "backend/data/processed"
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS Configuration
    allowed_origins: List[str] = [
        "chrome-extension://*",
        "moz-extension://*",
        "http://localhost:3000",
        "https://chess.com",
        "https://www.chess.com",
        "https://lichess.org"
    ]
    
    # Performance
    max_analysis_time: float = 10.0
    max_concurrent_analyses: int = 5
    cache_ttl: int = 300
    
    # Development
    reload: bool = True
    workers: int = 1
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def get_stockfish_path(self) -> str:
        """Get Stockfish path with fallback options"""
        if os.path.exists(self.stockfish_path):
            return self.stockfish_path
        
        # Fallback paths
        fallback_paths = [
            "stockfish.exe",
            "engines/stockfish.exe",
            "stockfish/stockfish.exe",
            "../stockfish/stockfish-windows-x86-64-avx2.exe",
            "../../stockfish/stockfish-windows-x86-64-avx2.exe"
        ]
        
        for path in fallback_paths:
            if os.path.exists(path):
                return path
        
        return self.stockfish_path  # Return original even if not found

settings = Settings()