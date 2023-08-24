""" Main module and entrypoint for the service."""
import os

import uvicorn
from fastapi import Depends, FastAPI

from api.routers import health_check
from config import logging_utils
from config.gcp_env import GCP_ENV_DATA
from config.service_config import SERVICE_CONFIG

logging_utils.init_logging(level=SERVICE_CONFIG.LOG_LEVEL, gcp_logging=GCP_ENV_DATA.IS_DEPLOYED)


# TODO: turn into cookiecutter template (with  mono-repo support (check git root / if in git repo))

# TODO: write readme and note tools used and why, note insipired by that config blog post, clean architecture, and 12 factor? with links?
# --> try to keep reamde light for projects add more to the parent repo

# TODO: add cloudbuild as CICD option, terraform for IAC?ss

# TODO: makedocs and makedocs-strs?

# TODO: update project from template scripts (in CLI)

# TODO: still need to first install typer to run CLI, which has the seutp command... cookiecuter post gen script? or pip dependancy?

# TODO: gitleaks? Requires docker or go...

# TODO: add some demo API models/routes (models/api/requests|responses, models/api/db/demo_db)


app = FastAPI(
    debug=True,
    title="TEMP_MY_SERVICE",
    description="TEMP_MY_DESCRIPTION",
    version="0.1.0",
    dependencies=[Depends(logging_utils.set_request_context)],
)


app.include_router(health_check.router)


if __name__ == "__main__":
    # This is used when running locally.
    # Uvicorn is used to run the application when deployed. See entrypoint in Dockerfile or Procfile.

    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080

    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
