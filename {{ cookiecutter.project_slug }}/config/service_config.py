""" Main Service Configuration Definition, ie service-wide constants and configurations - values to be specied via .env file and loaded in at runtime"""

import os
from enum import Enum

from pydantic import Field, constr
from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class LogLevel(str, Enum):
    """Log level options"""

    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class ServiceConfigModel(BaseSettings):
    """Main Service Configuration Definition, ie service-wide constants and configurations - values to be specied via .env file and loaded in at runtime"""

    model_config = SettingsConfigDict(
        str_strip_whitespace=True,
        extra="ignore",
        _env_file_encoding="utf-8",
        use_enum_values=True,
    )

    # Service
    SERVICE_NAME: str = Field(description="Service Name.")
    SERVICE_ENV: constr(to_lower=True) = Field(
        description="Service environment (ex. `prod`, `dev`, `test`, etc.)."
    )
    HEALTH_CHECK_ROUTE: str = Field(
        description="API Route to use as health check.", default="/healthcheck"
    )
    LOG_LEVEL: LogLevel = Field(default=LogLevel.INFO)

    # Deployment defaults
    DEFAULT_GCP_PROJECT: str = Field(
        description="Default GCP Project, used when deploying, etc."
    )
    DEFAULT_GCP_REGION: str = Field(
        description="Default GCP Region, used when deploying, etc."
    )
    DEFAULT_SERVICE_ACCOUNT_EMAIL: str = Field(
        description="Default GCP Service Account, used when deploying, etc."
    )

    # Can add other project-specific constants below


def get_service_config_path() -> str:
    """Get path of Service Config .env file, based on relative file path specified in an env variable."""
    try:
        service_config_file = os.environ["SERVICE_CONFIG_FILE"]

        # If specified value is not a file found in root directory, look for it in the ./config/service_configs dir
        if not os.path.isfile(service_config_file):
            service_config_file = os.path.join(
                ".", "config", "service_configs", service_config_file
            )

        # Raise if file not found
        assert os.path.isfile(service_config_file)
    except KeyError:
        raise FileNotFoundError(
            "Missing envrionment variable specifying service config file to use, export `SERVICE_CONFIG_FILE=my.env`."
        )
    except AssertionError:
        raise FileNotFoundError(
            f"Serivce Config file was not found at {service_config_file}"
        )
    return service_config_file


# Create service config model instance so it can be imported and referenced from the service app logic
SERVICE_CONFIG = ServiceConfigModel(_env_file=get_service_config_path())
