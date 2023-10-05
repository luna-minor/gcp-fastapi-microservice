"""Health check endpoint."""
from fastapi import APIRouter

from api.routers.core import BaseAPIRoute
from config.service_config import SERVICE_CONFIG

router = APIRouter(tags=["healthcheck"], route_class=BaseAPIRoute)


@router.get(SERVICE_CONFIG.HEALTH_CHECK_ROUTE)
def healthcheck():
    """Health Check Endpoint"""
    return {"message": "Service is up", "status": "OK"}
