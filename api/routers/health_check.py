"""Health check endpoint."""

from fastapi import APIRouter


router = APIRouter(
    prefix="/healthcheck",
    tags=["healthcheck"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def healthcheck():
    """Health Check Endpoint"""
    return {"message": "Service is up", "status": "OK"}
