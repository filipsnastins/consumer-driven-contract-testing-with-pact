from functools import lru_cache

from pydantic_settings import BaseSettings

from service_layer.tomodachi_bootstrap import TomodachiBaseSettings


class TomodachiAppSettings(TomodachiBaseSettings):
    dynamodb_table_name: str


class FastAPIAppSettings(BaseSettings):
    environment: str
    database_url: str

    @property
    def is_dev_env(self) -> bool:
        return self.environment in ["development", "autotest"]


@lru_cache
def get_tomodachi_app_settings() -> TomodachiAppSettings:
    return TomodachiAppSettings.model_validate({})


@lru_cache
def get_fastapi_app_settings() -> FastAPIAppSettings:
    return FastAPIAppSettings.model_validate({})
