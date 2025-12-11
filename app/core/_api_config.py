from dataclasses import dataclass
from functools import lru_cache

from starlette.config import Config
from starlette.datastructures import Secret


@dataclass
class ApiConfig:
    version:str = "0.0.1"
    name:str = "Transcription fichiers audio"
    api_prefix:str = ""
    api_key: Secret = "foobar"
    log_level: str = "debug"
    default_device:int = -1
    port: int = 8088
    ip: str = "localhost"

    def __post_init__(self):
        # load some parameters from .env
        config = Config(".env")
        self.api_key = config("API_KEY", cast=Secret)
        self.log_level = config("LOG_LEVEL")
        self.default_device = int(config("DEFAULT_DEVICE"))


# Singleton can be used for configuration
APICONFIG = ApiConfig()
