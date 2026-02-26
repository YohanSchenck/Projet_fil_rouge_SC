import asyncio
import os
import sys

sys.path.append(os.getcwd())
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, make_asgi_app

from app.api.v1 import API_ROUTERS
from app.core import APICONFIG
from app.services._batcher import batch_processor

origins = [
    "http://localhost",
    "http://localhost:4200",
]


# --- GESTION DU CYCLE DE VIE ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code exécuté au DEMARRAGE
    task = asyncio.create_task(batch_processor())
    print("Batch Processor démarré en arrière-plan.")
    
    yield  # Ici, l'application tourne...
    
    # Code exécuté à la FERMETURE
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("Batch Processor arrêté proprement.")

def get_app() -> FastAPI:
    fast_app = FastAPI(title=APICONFIG.name, version=APICONFIG.version, lifespan=lifespan)
    fast_app.include_router(API_ROUTERS, prefix=APICONFIG.api_prefix)
    fast_app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    metrics_app = make_asgi_app()
    fast_app.mount("/metrics", metrics_app)

    return fast_app

app = get_app()

if __name__ == "__main__":
    uvicorn.run(app,
                host=APICONFIG.ip,
                port=APICONFIG.port,
                log_level=APICONFIG.log_level,
                ws_ping_interval=2,
                ws_ping_timeout=2)

