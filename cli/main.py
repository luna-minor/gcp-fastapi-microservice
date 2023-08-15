import logging
import os
import subprocess
import sys
from typing import Optional

import typer
from typing_extensions import Annotated

logging.basicConfig(level=logging.INFO)

app = typer.Typer(
    name="TEMP_CLI",
    no_args_is_help=True,
)

CLI_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


@app.command()
def setup():
    """Setup a local dev envrionment. NOTE: it's a best practice to first create a virtual envrionment with your tool of choice (for ex. conda, venv, etc.)"""

    # TODO: when should you raise an error?

    # Install dev dependancies
    subprocess.run(args=[sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"])

    # Install pre-commit
    subprocess.run(args=[sys.executable, "-m", "pre_commit", "install"])

    # Run pre-commit
    subprocess.run(args=[sys.executable, "-m", "pre_commit", "run", "--all-files", "-v"])
    return


@app.command()
def lint():
    """Run linting and pre-commit commands"""
    # Run lininting checks and formatting via pre-commit
    subprocess.run(args=[sys.executable, "-m", "pre_commit", "run", "--all-files", "-v"])
    return


@app.command()
def start_dev_server(service_config_file: Annotated[str, typer.Argument(envvar="SERVICE_ENV_FILE")]):
    """Start serivce on localhost"""
    os.environ["SERVICE_ENV_FILE"] = service_config_file
    logging.info("Starting service on local server using config file: {}".format(service_config_file))
    resp = subprocess.run(args=[sys.executable, "-m", "main"])
    return


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def test(
    ctx: typer.Context, service_config_file: Annotated[str, typer.Argument(envvar="SERVICE_ENV_FILE")] = "local.yaml"
):
    """Run tests. Can specify"""
    os.environ["SERVICE_ENV_FILE"] = service_config_file
    logging.info("Running tests using config file: {}; with flags={}".format(service_config_file, ctx.args))
    extra_flags = ctx.args
    subprocess.run(args=[sys.executable, "-m", "pytest"] + extra_flags)
    return


@app.command()
def deploy(deploy: str):
    """Deploy service via a specified deployment script."""
    deploy_script_path = os.path.join(os.path.dirname(CLI_ROOT_DIR), "config", "deployments", deploy)

    # Ensure deployment script is executable
    subprocess.run(args=["chmod", "+x", deploy_script_path])

    # Run deployment script
    subprocess.run(args=[deploy_script_path])

    return


if __name__ == "__main__":
    app()
