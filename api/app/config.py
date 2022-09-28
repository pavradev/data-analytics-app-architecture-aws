from functools import lru_cache
from typing import Optional
from pydantic import BaseSettings
from passlib.hash import pbkdf2_sha256
class Settings(BaseSettings):
    admin_key_id: str
    admin_hashed_secret_key: str
    postgres_password: str
    postgres_server: str
    aws_endpoint_url: Optional[str]
    aws_default_region: str
    aws_access_key_id: str
    aws_secret_access_key: str

@lru_cache()
def get_settings():
    return Settings()
    