"""Main CLI interface for the project"""

import os
import subprocess
import sys
from typing import Optional

import typer
import yaml
from rich import print as rprint
from typing_extensions import Annotated

app = typer.Typer(
    name="TEMP_CLI",
    no_args_is_help=True,
)

CLI_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


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
def start_dev_server(service_config_file: Annotated[str, typer.Argument(envvar="SERVICE_ENV_FILE")] = "local.yaml"):
    """Start serivce on localhost."""

    os.environ["SERVICE_ENV_FILE"] = service_config_file

    rprint(f"Starting service on local server using config file: {service_config_file}")

    subprocess.run(args=[sys.executable, "-m", "main"], check=False)

    return


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def test(
    ctx: typer.Context, service_config_file: Annotated[str, typer.Argument(envvar="SERVICE_ENV_FILE")] = "local.yaml"
):
    """Run tests. NOTE: can specify extra command line flags and they will be passed to pytest."""

    os.environ["SERVICE_ENV_FILE"] = service_config_file

    rprint(f"Running tests using config file: {service_config_file}; with flags={ctx.args}")

    extra_flags = ctx.args

    subprocess.run(args=[sys.executable, "-m", "pytest"] + extra_flags, check=False)

    return


@app.command()
def deploy(deploy: str, service_config: str, version: Optional[str] = None, traffic_percent: int = 0):
    """Deploy service via a specified deployment script."""

    deploy_script_path = os.path.join(os.path.dirname(CLI_ROOT_DIR), "config", "deployments", deploy)
    service_config_path = os.path.join(os.path.dirname(CLI_ROOT_DIR), "config", "service_configs", service_config)

    # Load in service config and pass deployment flags
    with open(file=service_config_path, mode="r", encoding="utf-8") as service_config_file:
        service_config_data = yaml.safe_load(service_config_file)

    # Ensure deployment script is executable
    subprocess.run(args=["chmod", "+x", deploy_script_path], check=False)

    try:
        deployment_flags = [
            f"--gcp_project={service_config_data['GCP_PROJECT']}",
            f"--gcp_region={service_config_data['GCP_REGION']}",
            f"--service_name={service_config_data['SERVICE_NAME']}",
            f"--service_account={service_config_data['SERVICE_ACCOUNT_EMAIL']}",
            f"--service_env={service_config_data['SERVICE_ENV']}",
            f"--traffic_percent={traffic_percent}",
        ]
    except KeyError as exc:
        rprint(
            f"[bold red]Error! Missing required deployment flags from specified service config file {service_config}: {exc}[/bold red]"
        )
        raise typer.Abort()

    # Add optional values
    if version:
        deployment_flags.append(f"--version=${version}")

    # Run deployment script
    subprocess.run(args=[deploy_script_path] + deployment_flags, check=False)

    return


if __name__ == "__main__":
    app()
