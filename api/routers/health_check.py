"""Health check endpoint."""
from fastapi import APIRouter

from config.service_config import SERVICE_CONFIG

from api.routers.core import BaseAPIRoute

router = APIRouter(tags=["healthcheck"], route_class=BaseAPIRoute)


@router.get(SERVICE_CONFIG.HEALTH_CHECK_ROUTE)
def healthcheck():
    """Health Check Endpoint"""
    return {"message": "Service is up", "status": "OK"}
