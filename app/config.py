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
    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str
    REDIS_URL: str

    class Config:
        env_file = ".env"


settings = Settings()  # type: ignore
