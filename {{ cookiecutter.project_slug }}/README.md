# {{ cookiecutter.project_name }}
FastAPI Microservice designed for deployment on GCP Cloud Run.

{{ cookiecutter.project_description }}


## Prerequisites:
- [python](https://www.python.org/downloads/) and a virtual environment manager (recommended)
- [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/gcloud)
  - Note, if first time using gcloud, you may need to run the following commands to setup your local environment, can refer to the docs on [installing gcloud](https://cloud.google.com/sdk/docs/install)
    - `gcloud init`
    - `gcloud auth application-default login`
    - `gcloud auth login YOUR-EMAIL --update-adc`
- [docker](https://docs.docker.com/get-docker/) (for pre-commit hooks, etc.)


## Servcie
The service is structured as a [FastAPI](https://fastapi.tiangolo.com/) microservice
- OpenAPI Docs at `/docs`
- Health check at `/healthcheck` (configurable in [config/service_configs](configs/service_configs))
- API-specific code in [api](api)
    - Add new endpoints via [api/routers](api/routers)


## Setup
- (Recommended) Create/active a virtual environment
- `pip install -r requirements-dev.txt`
- The project comes with a CLI for things like testing, linting, deploying. Run below command to see commands.
    - `python cli/main.py --help`
    - Can extend the CLI by adding additional commands, built using [Typer](https://typer.tiangolo.com/).
- Setup local dev environment:
    - `python cli/main.py setup`


## Configuration
The [config](config) directory includes service config values and constants, as well as deployment settings.
- [service_config.py](config/service_config.py) contains the service runtime settings and constants, and is read in from a .env file specified via an enviornment variable `SERVICE_CONFIG_FILE=`, and validated via [pydantic](https://docs.pydantic.dev/latest/).
    - [service_configs](config/service_configs) contains the specific service config files used at runtime for the service, and settings used when deploying (ex. `dev.env`, `prod.env`, etc.)
- [gcp_env.py](config/gcp_env.py) loads certain values present when in a deployed GCP environment.
- [deployments](config/deployments/) contains deployment scripts.


## Test
- For base configuration see: [pyproject.toml](pyproject.toml)
- For options:
    - `python cli/main.py test --help`
- Run tests (added flags will be passed to pytest):
    - `python cli/main.py test`
    - Example passing extra pytest flags: `python cli/main.py tests -o log_cli=true log_cli_level=DEBUG`


## Lint
- For base configuration see: [pyproject.toml](pyproject.toml) and [.pre-commit-config.yaml](.pre-commit-config.yaml)
- Linting/formatting is automatically run using [pre-commit](https://pre-commit.com/)
- Manually run formatting and linting:
    - `python cli/main.py lint`
- [black](https://github.com/psf/black) for code formatting
- [isort](https://github.com/PyCQA/isort) for import sorting
- [gitleaks](https://github.com/gitleaks/gitleaks) for preventing committing secrets to version control


## Run locally
- For options:
    - `python cli/main.py start-dev-server --help`
- Run locally by starting a local dev server:
    - `python cli/main.py start-dev-server`


## Deploy
- For options:
    - `python cli/main.py deploy --help`
- To deploy:
    - `python cli/main.py deploy DEPLOY_SCRIPT`
    - `--traffic-percent`: optional flag to specify percentage of traffic new version should accept (defaults to 0%)
    - `--version`: optional flag to specify a verion name
    - Ex. `python cli/main.py deploy deploy_gcr.sh --traffic-percent=50`