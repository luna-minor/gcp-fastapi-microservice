""" Main module and entrypoint for the service."""
import logging
import os

import uvicorn
from fastapi import FastAPI

from api.routers import health_check
from config.gcp_env import GCP_ENV_DATA
from config.service_config import SERVICE_CONFIG

logging.basicConfig(level=logging.INFO)

if GCP_ENV_DATA.IS_DEPLOYED:
    import google.cloud.logging

    gcp_log_client = google.cloud.logging.Client()
    gcp_log_client.setup_logging()


# TODO: test deployment concurrency settings work with given Procfile
# https://cloud.google.com/blog/topics/developers-practitioners/build-chat-server-cloud-run
# https://towardsdatascience.com/deploy-a-dockerized-fastapi-app-to-google-cloud-platform-24f72266c7ef

# TODO: improve logging so uses json format to match gcp log payloads (locally logs to console?)

# TODO: add some demo API models/routes (where to place?)

# TODO: turn into cookiecutter template

# TODO: write readme and note tools used and why, note insipired by that config blog post, clean architecture, and 12 factor? with links?
# --> try to keep reamde light for projects add more to the parent repo

# TODO: makedocs and makedocs-strs?

# TODO: mono-repo support (check git root / if in git repo)

# TODO: update project from template scripts (in CLI)

# TODO: still need to first install typer to run CLI, which has the seutp command... cookiecuter post gen script? or pip dependancy?

# TODO: gitleaks? Requires docker or go...

app = FastAPI(
    debug=True,
    title="TEMP_MY_SERVICE",
    description="TEMP_MY_DESCRIPTION",
    version="0.1.0",
)


app.include_router(health_check.router)


if __name__ == "__main__":
    # This is used when running locally.
    # Uvicorn is used to run the application when deployed. See entrypoint in Dockerfile or Procfile.

    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080

    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
