from functools import lru_cache

from tomodachi_bootstrap import TomodachiBaseSettings


class Settings(TomodachiBaseSettings):
    dynamodb_table_name: str


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
