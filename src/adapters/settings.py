from functools import lru_cache

from pydantic_settings import BaseSettings

from service_layer.tomodachi_bootstrap import TomodachiBaseSettings


class TomodachiAppSettings(TomodachiBaseSettings):
    DYNAMODB_TABLE_NAME: str


class FastAPIAppSettings(BaseSettings):
    DATABASE_URL: str


@lru_cache
def get_tomodachi_app_settings() -> TomodachiAppSettings:
    return TomodachiAppSettings.model_validate({})


@lru_cache
def get_fastapi_app_settings() -> FastAPIAppSettings:
    return FastAPIAppSettings.model_validate({})
