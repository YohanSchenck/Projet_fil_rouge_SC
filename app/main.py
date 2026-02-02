import os
import sys

sys.path.append(os.getcwd())
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1 import API_ROUTERS
from app.core import APICONFIG

origins = [
    "http://localhost",
    "http://localhost:4200",
]


def get_app() -> FastAPI:
    fast_app = FastAPI(title=APICONFIG.name, version=APICONFIG.version)
    fast_app.include_router(API_ROUTERS, prefix=APICONFIG.api_prefix)
    fast_app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    Instrumentator().instrument(fast_app).expose(fast_app)
    return fast_app



app = get_app()



if __name__ == "__main__":
    uvicorn.run(app,
                host=APICONFIG.ip,
                port=APICONFIG.port,
                log_level=APICONFIG.log_level,
                ws_ping_interval=2,
                ws_ping_timeout=2)
