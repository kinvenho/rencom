from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import logging

class Settings(BaseSettings):
    # App
    app_name: str = "Rencom"
    debug: bool = False
    version: str = "1.0.0"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Supabase
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_anon_key: str = Field(..., env="SUPABASE_ANON_KEY")
    supabase_service_key: str = Field(..., env="SUPABASE_SERVICE_KEY")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    cors_origins: List[str] = ["*"]

    def validate(self):
        missing = []
        # List of required keys
        required = [
            ("supabase_url", self.supabase_url),
            ("supabase_anon_key", self.supabase_anon_key),
            ("supabase_service_key", self.supabase_service_key),
            ("secret_key", self.secret_key),
        ]
        for name, value in required:
            if not value or (isinstance(value, str) and not value.strip()):
                missing.append(name)
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
        # Optional: Add format checks (e.g., URL)
        if not self.supabase_url.startswith("http"):
            raise RuntimeError("supabase_url must be a valid URL (start with http or https)")
        logging.info("All required environment variables are present and valid.")

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
settings.validate() 