"""Health check endpoint."""
from fastapi import APIRouter

from .core import LoggingRoute

router = APIRouter(
    tags=["healthcheck"],
    route_class=LoggingRoute
)


@router.get("/healthcheck")
def healthcheck():
    """Health Check Endpoint"""
    return {"message": "Service is up", "status": "OK"}
