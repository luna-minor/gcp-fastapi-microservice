""" Main module and entrypoint for the service."""

import uvicorn
from fastapi import FastAPI
from api.routers import health_check


app = FastAPI(
    debug=False,
    title="MY_SERVICE",
    description="MY_DESCRIPTION",
    version="0.1.0",
)


app.include_router(health_check.router)

@app.get("/")
def root():
    """Root endpiont"""
    return {"message": "Service is up", "status": "OK"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
