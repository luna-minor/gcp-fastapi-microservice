""" Main module and entrypoint for the service."""
import os

import uvicorn
from api.routers import health_check
from config import logging_utils
from config.gcp_env import GCP_ENV_DATA
from config.service_config import SERVICE_CONFIG
from fastapi import Depends, FastAPI

logging_utils.init_logging(
    level=SERVICE_CONFIG.LOG_LEVEL, gcp_logging=GCP_ENV_DATA.IS_DEPLOYED
)


app = FastAPI(
    debug=True,
    title="{{ cookiecutter.project_slug }}",
    description="{{ cookiecutter.project_description }}",
    version="0.1.0",
    dependencies=[Depends(logging_utils.set_request_context)],
)


app.include_router(health_check.router)


if __name__ == "__main__":
    # This is used when running locally.
    # Uvicorn is used to run the application when deployed. See entrypoint in Dockerfile or Procfile.

    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080

    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
