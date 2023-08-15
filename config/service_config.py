""" Main Service Configuration Definition, ie service-wide constants and configurations - values to be specied via yaml files and loaded in at runtime"""

import os

import yaml
from pydantic import BaseModel, DirectoryPath, Field

# TODO: What is a application config.py / python globals - vs - shared variables in terraform - vs - env values from runtime env....


class ServiceConfigModel(BaseModel):
    """Service-wide constants and configurations loaded at runtime."""

    # Service deployed env values, set automatically
    SERVICE_ID: str = Field(description="Service ID from deployed environment, automatically set.")
    SERVICE_VERSION: str = Field(description="Service version from deployed environment, automatically set.")
    SERVICE_ROOT_DIR: DirectoryPath = Field(description="Root dir of the service.")

    # Service
    SERVICE_NAME: str = Field(description="Service Name.")
    SERVICE_INSTANCE: str = Field(description="Service instances (ex. `prod`, `dev`, `test`, etc.).")
    SERVICE_ACCOUNT_EMAIL: str = Field(description="Service Account email the service acts as.")
    HEALTH_CHECK_ROUTE: str = Field(description="API Route to use as health check.", default="/healthcheck")

    # GCP
    GCP_PROJECT: str = Field(description="Main GCP Project for resources and deployments.")
    GCP_REGION: str = Field(description="Default GCP Region to use for resources and deployments")


# Determine deployed GCP env values. Accoutning for GKE, Cloud Run, Cloud Functions, and App Engine environments.
service_env_data = {}
service_env_data["SERVICE_ID"] = (
    os.environ.get("K_SERVICE") or os.environ.get("FUNCTION_NAME") or os.environ.get("GAE_SERVICE") or "not-set"
)
service_env_data["SERVICE_VERSION"] = (
    os.environ.get("K_REVISION")
    or os.environ.get("GAE_VERSION")
    or os.environ.get("X_GOOGLE_FUNCTION_VERSION")
    or "not-set"
)
service_env_data["SERVICE_ROOT_DIR"] = os.path.dirname(os.path.abspath(__file__))


# Load in Service Config from yaml file, based on relative file path specified in an env variable.
class MissingServiceConfig(Exception):
    pass


try:
    SERVICE_ENV_FILE = os.environ["SERVICE_ENV_FILE"]
except KeyError:
    raise MissingServiceConfig(
        "Missing envrionment variable specifying service config file to use, export `SERVICE_ENV_FILE=ex_file.yaml`."
    )


with open(
    file=os.path.join(service_env_data["SERVICE_ROOT_DIR"], "service_envs", SERVICE_ENV_FILE),
    mode="r",
    encoding="utf-8",
) as service_config_file:
    service_config_data = yaml.safe_load(service_config_file)

    # Create service config model instance so it can be imported and referenced from the service application logic
    SERVICE_CONFIG = ServiceConfigModel.model_validate({**service_config_data, **service_env_data})
