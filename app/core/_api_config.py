from dataclasses import dataclass
from functools import lru_cache

from starlette.config import Config
from starlette.datastructures import Secret


@dataclass
class ApiConfig:
    version: str = "1.0.0" # Tu peux passer en 1.0 !
    name: str = "Transcription fichiers audio"
    api_prefix: str = ""
    log_level: str = "info"
    port: int = 8088
    ip: str = "localhost" # Préférable pour Docker

    def __post_init__(self):
        config = Config(".env")
        self.api_key = config("API_KEY", cast=Secret)
        self.log_level = config("LOG_LEVEL", default="info")

# Singleton can be used for configuration
APICONFIG = ApiConfig()
