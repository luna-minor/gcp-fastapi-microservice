""" Main module and entrypoint for the service."""
import logging

import uvicorn
from fastapi import FastAPI

from api.routers import health_check

logging.basicConfig(level=logging.DEBUG)


# TODO: test deployment concurrency settings work with given Procfile
# https://cloud.google.com/blog/topics/developers-practitioners/build-chat-server-cloud-run
# https://towardsdatascience.com/deploy-a-dockerized-fastapi-app-to-google-cloud-platform-24f72266c7ef

# TODO: improve logging so uses json format to match gcp log payloads (locally logs to console?)

# TODO: add some demo API models/routes (where to place?)

# TODO: turn into cookiecutter template

# TODO: write readme and note tools used and why

# TODO: makedocs and makedocs-strs?

# TODO: mono-repo support (check git root / if in git repo)

app = FastAPI(
    debug=True,
    title="TEMP_MY_SERVICE",
    description="TEMP_MY_DESCRIPTION",
    version="0.1.0",
)


app.include_router(health_check.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
