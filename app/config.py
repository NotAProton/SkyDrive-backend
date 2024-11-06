from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    API_V1_PREFIX: str
    PROJECT_NAME: str
    BACKEND_CORS_ORIGINS: List[str]
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SECRET_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
