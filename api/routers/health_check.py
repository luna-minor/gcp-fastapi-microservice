"""Health check endpoint."""
from fastapi import APIRouter

from config.service_config import SERVICE_CONFIG

from .core import LoggingRoute

router = APIRouter(tags=["healthcheck"], route_class=LoggingRoute)


@router.get(SERVICE_CONFIG.HEALTH_CHECK_ROUTE)
def healthcheck():
    """Health Check Endpoint"""
    return {"message": "Service is up", "status": "OK"}
