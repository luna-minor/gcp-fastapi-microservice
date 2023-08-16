""" Main Service Configuration Definition, ie service-wide constants and configurations - values to be specied via yaml files and loaded in at runtime"""

import logging
import os
from functools import lru_cache

import requests
import yaml
from pydantic import BaseModel, ConfigDict, DirectoryPath, Field, constr


class ServiceConfigModel(BaseModel):
    """Service-wide constants and configurations loaded at runtime."""

    model_config = ConfigDict(str_strip_whitespace=True, frozen=True, extra="allow")

    # Service
    SERVICE_NAME: str = Field(description="Service Name.")
    SERVICE_ENV: constr(to_upper=True) = Field(description="Service environment (ex. `prod`, `dev`, `test`, etc.).")
    SERVICE_ACCOUNT_EMAIL: str = Field(description="Service Account email the service acts as.")
    HEALTH_CHECK_ROUTE: str = Field(description="API Route to use as health check.", default="/healthcheck")

    # Service deployed env values, set automatically
    SERVICE_ID: str = Field(description="Service ID from deployed environment, automatically set.")
    SERVICE_VERSION: str = Field(description="Service version from deployed environment, automatically set.")
    SERVICE_ROOT_DIR: DirectoryPath = Field(description="Root dir of the service.")

    # GCP, set automatically when in a deployed envrionment
    GCP_PROJECT: str = Field(description="Main GCP Project for resources and deployments.")
    GCP_REGION: str = Field(description="Default GCP Region to use for resources and deployments")


@lru_cache(maxsize=2)
def get_gcp_env_data() -> dict:
    """Load deployed GCP envrionment data, from env vars and fetched from metadata server."""

    gcp_metadata_server_url = "http://metadata.google.internal"
    gcp_metadata_server_headers = {"Metadata-Flavor": "Google"}
    gcp_metadata_timeout = 5

    gcp_env_data = {}

    # Determine deployed GCP env values. Accoutning for GKE, Cloud Run, Cloud Functions, and App Engine environments.
    gcp_env_data["SERVICE_ID"] = (
        os.environ.get("K_SERVICE") or os.environ.get("GAE_SERVICE") or os.environ.get("FUNCTION_NAME") or "not-set"
    )
    gcp_env_data["SERVICE_VERSION"] = (
        os.environ.get("K_REVISION")
        or os.environ.get("GAE_VERSION")
        or os.environ.get("X_GOOGLE_FUNCTION_VERSION")
        or "not-set"
    )
    gcp_env_data["SERVICE_ROOT_DIR"] = os.path.dirname(os.path.abspath(__file__))

    if gcp_env_data["SERVICE_ID"] != "not-set":
        resp = requests.get(
            gcp_metadata_server_url + "/computeMetadata/v1/instance/region",
            headers=gcp_metadata_server_headers,
            timeout=gcp_metadata_timeout,
        )
        logging.info(resp.content)
        logging.info(resp.json())
        gcp_env_data["GCP_PROJECT"] = requests.get(
            gcp_metadata_server_url + "/computeMetadata/v1/project/project-id",
            headers=gcp_metadata_server_headers,
            timeout=gcp_metadata_timeout,
        )
        gcp_env_data["GCP_REGION"] = requests.get(
            gcp_metadata_server_url + "/computeMetadata/v1/instance/region",
            headers=gcp_metadata_server_headers,
            timeout=gcp_metadata_timeout,
        )
        gcp_env_data["SERVICE_ACCOUNT_EMAIL"] = requests.get(
            gcp_metadata_server_url + "/computeMetadata/v1/instance/service-accounts/default/email",
            headers=gcp_metadata_server_headers,
            timeout=gcp_metadata_timeout,
        )

    return gcp_env_data


# Load in Service Config from yaml file, based on relative file path specified in an env variable.
try:
    SERVICE_ENV_FILE = os.environ["SERVICE_ENV_FILE"]
except KeyError as exc:
    raise FileNotFoundError(
        "Missing envrionment variable specifying service config file to use, export `SERVICE_ENV_FILE=ex_file.yaml`."
    ) from exc

GCP_ENV_DATA = get_gcp_env_data()

with open(
    file=os.path.join(GCP_ENV_DATA["SERVICE_ROOT_DIR"], "service_configs", SERVICE_ENV_FILE),
    mode="r",
    encoding="utf-8",
) as service_config_file:
    service_config_data = yaml.safe_load(service_config_file)

    # Override any overlapping service config values from the GCP envrionment if present
    service_config_data = {**service_config_data, **GCP_ENV_DATA}

    # Create service config model instance so it can be imported and referenced from the service application logic
    SERVICE_CONFIG = ServiceConfigModel.model_validate(service_config_data)
