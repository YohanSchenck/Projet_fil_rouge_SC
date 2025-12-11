from contextlib import asynccontextmanager

from app.ressources import get_model
from fastapi import FastAPI

from ._api_config import APICONFIG


@asynccontextmanager
async def model_lifespan(application: FastAPI):
    model = get_model(APICONFIG.default_device) # Init the model
    yield
    del model
    get_model.cache_clear() # clear the lru cache
