from app.routers import transcription
from fastapi import APIRouter

"""
Router of the API. It registers the routes and it prefix's. 
The openAPI documentation is automatically updated.
"""
API_ROUTERS = APIRouter()


API_ROUTERS.include_router(transcription.router, tags=["transcription"])
