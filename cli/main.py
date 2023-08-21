"""Main CLI interface for the project"""

import os
import subprocess
import sys
from typing import Optional

import typer
from rich import print as rprint
from typing_extensions import Annotated

app = typer.Typer(
    name="TEMP_CLI",
    no_args_is_help=True,
)

CLI_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Fetch list of deployment scripts and service configs for CLI help
DEPLOYMENT_SCRIPTS = os.listdir(os.path.join(os.path.dirname(CLI_ROOT_DIR), "config", "deployments"))
SERVICE_CONFIGS = os.listdir(os.path.join(os.path.dirname(CLI_ROOT_DIR), "config", "service_configs"))


@app.command()
def setup():
    """Setup a local dev envrionment.
    NOTE: it's a best practice to first create a virtual envrionment with your tool of choice (for ex. conda, venv, etc.)
    """

    # Install dev dependancies
    pip_resp = subprocess.run(args=[sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"], check=False)

    if pip_resp.returncode != 0:
        raise typer.Abort()

    # Install pre-commit
    pre_commit_install_resp = subprocess.run(args=[sys.executable, "-m", "pre_commit", "install"], check=False)

    if pre_commit_install_resp.returncode != 0:
        raise typer.Abort()

    # Run pre-commit
    pre_commit_run_resp = subprocess.run(
        args=[sys.executable, "-m", "pre_commit", "run", "--all-files", "-v"], check=False
    )

    if pre_commit_run_resp.returncode != 0:
        rprint(
            "[bold red]Linting/Formatting Error![/bold red] [green]Project is sucessfully setup, can run the `lint` CLI command to run the formatting and lint checks.[/green]"
        )

    rprint("=" * 100)
    rprint("[green]Finished project setup! :tada:")
    rprint("=" * 100)
    return


@app.command()
def lint():
    """Run linting and pre-commit commands"""
    # Run lininting checks and formatting via pre-commit
    subprocess.run(args=[sys.executable, "-m", "pre_commit", "run", "--all-files", "-v"], check=False)
    return


@app.command()
def start_dev_server(
    service_config_file: Annotated[
        str, typer.Argument(envvar="SERVICE_CONFIG_FILE")
    ] = "config/service_configs/local.env"
):
    """Start serivce on localhost."""

    os.environ["SERVICE_CONFIG_FILE"] = service_config_file

    rprint(f"Starting service on local server using config file: {service_config_file}")

    subprocess.run(args=[sys.executable, "-m", "main"], check=False)

    return


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def test(
    ctx: typer.Context,
    service_config_file: Annotated[
        str, typer.Argument(envvar="SERVICE_CONFIG_FILE")
    ] = "config/service_configs/local.env",
):
    """Run tests. NOTE: can specify extra command line flags and they will be passed to pytest."""

    os.environ["SERVICE_CONFIG_FILE"] = service_config_file

    rprint(f"Running tests using config file: {service_config_file}; with flags={ctx.args}")

    extra_flags = ctx.args

    subprocess.run(args=[sys.executable, "-m", "pytest"] + extra_flags, check=False)

    return


@app.command()
def deploy(
    deploy: Annotated[str, typer.Argument(help=f"Options: {DEPLOYMENT_SCRIPTS}")],
    service_config: Annotated[str, typer.Argument(help=f"Options: {SERVICE_CONFIGS}")],
    version: Optional[str] = None,
    traffic_percent: int = 0,
):
    """Deploy service via a specified deployment script."""
    deployment_script = os.path.join(os.path.dirname(CLI_ROOT_DIR), "config", "deployments", deploy)

    # If service config is listed in the options, build full path, else use file specified
    if service_config in SERVICE_CONFIGS:
        service_config = os.path.join(os.path.dirname(CLI_ROOT_DIR), "config", "service_configs", service_config)

    if not os.path.isfile(service_config):
        raise FileNotFoundError("Service config not found at {}".format(service_config))

    # Ensure deployment script is executable
    subprocess.run(args=["chmod", "+x", deployment_script], check=False)

    # Build deployment flags
    deployment_flags = [
        f"--service_config={service_config}",
        f"--traffic_percent={traffic_percent}",
    ]
    if version:
        deployment_flags.append(f"--version=${version}")

    # Run deployment script
    deploy_resp = subprocess.run(args=[deployment_script] + deployment_flags, check=False)

    if deploy_resp.returncode != 0:
        rprint("[bold red]Deployment Error![/bold red]")
        typer.Abort()

    return


if __name__ == "__main__":
    app()
