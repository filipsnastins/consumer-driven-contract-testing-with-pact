from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str


@lru_cache
def get_settings() -> Settings:
    return Settings.model_validate({})
