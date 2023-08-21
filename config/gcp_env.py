"""File to load in deployed environment values"""

import os
from functools import lru_cache
from typing import Annotated

import requests
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

DEAULT_STR_VALUE = "not-set"


class DeployedEnvData(BaseModel):
    """Class with deployed envrionment data"""

    model_config = ConfigDict(str_strip_whitespace=True)

    IS_DEPLOYED: bool = Field(description="True if in a deployed environment (not loal)", default=False)

    GCP_PROJECT: str = Field(description="GCP Project from env", default=DEAULT_STR_VALUE)
    GCP_REGION: str = Field(description="GCP Region from env", default=DEAULT_STR_VALUE)
    SERVICE_ID: str = Field(description="Service ID from env", default=DEAULT_STR_VALUE)
    SERVICE_VERSION: str = Field(description="Service version from env", default=DEAULT_STR_VALUE)
    SERVICE_ACCOUNT_EMAIL: str = Field(description="Serivce Accountfrom env", default=DEAULT_STR_VALUE)


@lru_cache(maxsize=2)
def load_deployed_env_data() -> DeployedEnvData:
    """Load deployed GCP envrionment data, from env vars and fetched from metadata server."""

    gcp_metadata_server_url = "http://metadata.google.internal"
    gcp_metadata_server_headers = {"Metadata-Flavor": "Google"}
    gcp_metadata_timeout = 5

    # Determine deployed GCP env values. Accoutning for GKE, Cloud Run, Cloud Functions, and App Engine environments.
    service_id = os.environ.get("K_SERVICE") or os.environ.get("GAE_SERVICE") or os.environ.get("FUNCTION_NAME")
    service_version = (
        os.environ.get("K_REVISION") or os.environ.get("GAE_VERSION") or os.environ.get("X_GOOGLE_FUNCTION_VERSION")
    )

    # If service ID is present, consider deployed env and load other values
    if not service_id:
        return DeployedEnvData(IS_DEPLOYED=False)

    gcp_project = requests.get(
        gcp_metadata_server_url + "/computeMetadata/v1/project/project-id",
        headers=gcp_metadata_server_headers,
        timeout=gcp_metadata_timeout,
    ).content.decode("utf-8")

    gcp_region = requests.get(
        gcp_metadata_server_url + "/computeMetadata/v1/instance/region",
        headers=gcp_metadata_server_headers,
        timeout=gcp_metadata_timeout,
    ).content.decode("utf-8")

    service_account = requests.get(
        gcp_metadata_server_url + "/computeMetadata/v1/instance/service-accounts/default/email",
        headers=gcp_metadata_server_headers,
        timeout=gcp_metadata_timeout,
    ).content.decode("utf-8")

    return DeployedEnvData(
        IS_DEPLOYED=True,
        SERVICE_ID=service_id,
        SERVICE_VERSION=service_version,
        GCP_PROJECT=gcp_project,
        GCP_REGION=gcp_region,
        SERVICE_ACCOUNT_EMAIL=service_account,
    )


# Load in GCP env data, if deployed
GCP_ENV_DATA = load_deployed_env_data()
