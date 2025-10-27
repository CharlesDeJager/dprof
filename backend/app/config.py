from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Threading and performance settings
    max_threads: int = 4
    default_max_records: int = 10000
    chunk_size: int = 1000
    
    # Database settings
    oracle_client_path: Optional[str] = None
    
    # File upload settings
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    temp_dir: str = "temp"
    
    # Export settings
    export_dir: str = "exports"
    
    class Config:
        env_file = ".env"
        env_prefix = "DVIEW_"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Ensure directories exist
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.export_dir, exist_ok=True)