# GCP Fastapi Microservice

A template [FastAPI](https://fastapi.tiangolo.com/) Microservice designed for deployment on GCP Cloud Run, built with [Cookiecutter](https://github.com/cookiecutter/cookiecutter). It provides a simple yet solid foundation for developing scalable and maintainable microservices adhering to common best practices. Inspiration taken from the principles in the [12 Factor App](https://12factor.net/) and Clean Architecture.


## Features:
- Integrated Logging and Tracing in GCP
- API Request / Response validation with Pydantic / FastAPI
- Automated Open API Spec generation via FastAPI
- Separation of configuration and application logic
- Configurable linting and code formatting, enforced via pre-commit hooks
- Helper CLI to setup, test, run, lint, and deploy service


## Prerequisites:
- [python](https://www.python.org/downloads/) and a virtual environment manager (recommended)
- [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/gcloud) (for deployments and interacting with GCP)
  - Note, if first time using gcloud, you may need to run the following commands to setup your local environment, can refer to the docs on [installing gcloud](https://cloud.google.com/sdk/docs/install)
    - `gcloud init`
    - `gcloud auth application-default login`
    - `gcloud auth login YOUR-EMAIL --update-adc`
- [docker](https://docs.docker.com/get-docker/) (for pre-commit hooks, etc.)


## Usage
- Run the below command in the parent directory you want to create the project in.
    - `cookiecutter https://github.com/luna-minor/gcp-fastapi-microservice`
- A new project will be generated with a simple readme containing more detailed info on testing, logging, deploying, etc.


## Project Structure:
```
.
├── api
│   ├── routers
│   │   ├── __init__.py
│   │   ├── core.py
│   │   └── health_check.py
│   └── __init__.py
├── cli
│   ├── __init__.py
│   └── main.py
├── config
│   ├── deployments
│   │   └── deploy_gcr.sh
│   ├── service_configs
│   │   ├── dev.env
│   │   ├── local.env
│   │   └── prod.env
│   ├── __init__.py
│   ├── gcp_env.py
│   ├── logging_utils.py
│   └── service_config.py
├── tests
│   ├── integration
│   │   └── __init__.py
│   └── unit
│       ├── __init__.py
│       └── test_healthcheck.py
├── .cookiecutter.json
├── .coverage
├── .gcloudignore
├── .gitattributes
├── .gitignore
├── .gitleaks.toml
├── .pre-commit-config.yaml
├── .python-version
├── Procfile
├── README.md
├── main.py
├── pyproject.toml
├── requirements-dev.txt
└── requirements.txt
```


## Configuration
The [config](config) directory includes service config values and constants, as well as deployment settings.
- [service_config.py](config/service_config.py) contains the service runtime settings and constants, and is read in from a .env file specified via an enviornment variable `SERVICE_CONFIG_FILE=`, and validated via [pydantic](https://docs.pydantic.dev/latest/).
    - [service_configs](config/service_configs) contains the specific service config files used at runtime for the service, and settings used when deploying (ex. `dev.env`, `prod.env`, etc.)
- [gcp_env.py](config/gcp_env.py) loads certain values present when in a deployed GCP environment.
- [deployments](config/deployments/) contains deployment scripts.


## Opinions
- Why aren't the .env files gitignored? - this service takes the opinion that .env files are useful for configuration of a service and enables easily chanigng those values for different enviornments - all useful things to have comitted into source control. Any secrets needed should be managed via a secret manager and fetched at runtime, rather than set in a static configuration file. So instead of specifying an API key or SQL connection secret in the .env file - instead the .env should specify the URI or ID or path where a secret can be securely fetched. 


## References

### Tools
- [Pydantic](https://docs.pydantic.dev/latest/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Typer CLI](https://typer.tiangolo.com/)
- [Cookiecutter](https://cookiecutter.readthedocs.io/en/stable/)
- [Black](https://github.com/psf/black)
- [isort](https://pycqa.github.io/isort/)
- [pre-commit](https://pre-commit.com/)
- [Gitleaks](https://github.com/gitleaks/gitleaks)
- [Docker](https://docs.docker.com/get-docker/)
- [Google Cloud SDK](https://cloud.google.com/cli)

### Articles
- [12 Factor App](https://12factor.net/)
- [Intro to Clean Architecture](https://betterprogramming.pub/the-clean-architecture-beginners-guide-e4b7058c1165)
- [FastAPI Clean Architecture](https://medium.com/@YDyachenko/fastapi-clean-architecture-4c961b512213)
- [Abstraction and Limiting Information flow](https://betterprogramming.pub/abstraction-and-limiting-information-flow-550e23931d25)