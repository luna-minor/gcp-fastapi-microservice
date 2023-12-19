"""CLI interface for managing Cloud Build"""

import os
import subprocess
from glob import glob
from urllib import parse

import typer
import yaml
from config.service_config import SERVICE_CONFIG
from rich import print as rprint
from typing_extensions import Annotated

app = typer.Typer(
    name="cloudbuild-cli",
    no_args_is_help=True,
)

CLOUD_BUILD_CLI_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_GCP_PROJECT = SERVICE_CONFIG.DEFAULT_GCP_PROJECT


@app.command()
def manual_build(
    project_id: Annotated[
        str, typer.Argument(help="GCP Project ID to create Build job in.")
    ] = DEFAULT_GCP_PROJECT
):
    """Manually trigger a remote build in Cloud Build."""
    # Build Subsitution varibales
    short_sha = "manual-build"
    branch_name_resp = subprocess.run(args=["git", "branch", "--show-current"])
    if branch_name_resp.returncode != 0:
        rprint("[bold red][/bold red]")
    branch_name = branch_name_resp.stdout.decode("utf-8").strip()

    # Use gcloud CLI to submit build
    # https://cloud.google.com/sdk/gcloud/reference/builds/submit
    build_cmd = ["gcloud", "builds", "submit", "."]
    build_flags = [
        "--config=./cloudbuild/cloudbuild.yaml",
        f"--project=${project_id}",
        f"--substitutions BRANCH_NAME={branch_name},SHORT_SHA={short_sha}",
    ]
    build_resp = subprocess.run(
        args=build_cmd + build_flags,
        check=False,
    )

    if build_resp.returncode != 0:
        rprint("[bold red]Remote Build running in Cloud Build failed![/bold red]")
        typer.Abort()

    rprint("=" * 100)
    rprint("[green]Finished remote build! :tada:")
    rprint("=" * 100)
    return


@app.command()
def setup(
    project_id: Annotated[
        str, typer.Argument(help="GCP Project ID to create Build job in.")
    ] = DEFAULT_GCP_PROJECT
):
    """Create the Cloud Build Triggers to connect GitHub Repository events with Cloud Build.
    NOTE: Requires a one-time manual linking between Cloud Build and GitHub, will be prompted via the gcloud CLI if this is needed.
    NOTE: Will create/update any build triggers defined in the cloudbuild directory ending in "_trigger.yaml"
    """
    # Fetch Git Repo Owner from orgin ULRL
    git_remote_origin_resp = subprocess.run(
        args=["git", "config", "--get remote.origin.url"]
    )
    if git_remote_origin_resp.returncode != 0:
        rprint(
            "[bold red]Failed to fetch git repo's remote origin URL, to setup Cloud Build the project must be in a published Git Repo.[/bold red]"
        )
        typer.Abort()

    # Find/replace Git Repo Owner text placeholder in trigger configs
    git_remote_origin = git_remote_origin_resp.stdout.decode("utf-8").strip()
    git_remote_owner = parse(git_remote_origin).path.split("/")[1]

    cloudbuild_files = [
        "cloudbuild/cloudbuild.yaml",
        "cloudbuild/pr_main_trigger.yaml",
        "cloudbuild/push_main_trigger.yaml",
    ]
    for cb_file in cloudbuild_files:
        with open(cb_file, "r") as file:
            file_text = file.read()
            file_text = file_text.replace(
                "TEMP_PLACEHOLDER_GIT_OWNER", git_remote_owner
            )

        with open(cb_file, "w") as file:
            file.write(file_text)

    # Use file naming convetion to fetch all trigger config YAML files
    trigger_configs = glob("./cloudbuild/*_trigger.yaml")

    failed_triggers = []
    for trigger_file in trigger_configs:
        # Import trigger (create/update)
        # https://cloud.google.com/sdk/gcloud/reference/beta/builds/triggers/import
        trigger_command = [
            "gcloud",
            "builds",
            "triggers",
            "import",
            f"--source=${trigger_file}",
            f"project={project_id}",
        ]
        trigger_resp = subprocess.run(
            args=trigger_command,
            check=False,
        )

        if trigger_resp.returncode != 0:
            rprint(
                f"[bold red]Failed to create Build Trigger with configuration at: {trigger_file}[/bold red]"
            )
            failed_triggers.append(trigger_file)

    rprint("=" * 100)
    rprint("[green]Finished Cloud Build Triggers setup/update! :tada:")
    if len(failed_triggers) > 0:
        rprint(
            f"[bold red]NOTE: {len(failed_triggers)}/{len(trigger_configs)} build trigger files failed.[/bold red]"
        )
        rprint(
            "[bold red]Failed trigger configs: {}[/bold red]".format(
                "\n".join(failed_triggers)
            )
        )
    rprint("=" * 100)
    return


@app.command()
def update_build_trigger(
    project_id: Annotated[
        str, typer.Argument(help="GCP Project ID to create Build job in.")
    ] = DEFAULT_GCP_PROJECT,
    build_trigger: Annotated[
        str,
        typer.Argument(
            help="Specific Build Trigger configuration file to create/update. Use 'all' to create/update all trigger files."
        ),
    ] = "all",
):
    """Update one or all Build Trigger configs
    NOTE: Will create/update any build triggers defined in the cloudbuild directory ending in "_trigger.yaml"
    """

    # Run setup command to create/update all Build Triggers
    if build_trigger == "all":
        setup(project_id=project_id)
        return

    # Import trigger (create/update)
    # https://cloud.google.com/sdk/gcloud/reference/beta/builds/triggers/import
    trigger_command = [
        "gcloud",
        "builds",
        "triggers",
        "import",
        f"--source=${build_trigger}",
        f"project={project_id}",
    ]
    trigger_resp = subprocess.run(
        args=trigger_command,
        check=False,
    )

    if trigger_resp.returncode != 0:
        rprint(
            f"[bold red]Failed to create Build Trigger with configuration at: {build_trigger}[/bold red]"
        )
        raise typer.Abort()

    rprint("=" * 100)
    rprint("[green]Finished Cloud Build Triggers setup/update! :tada:")
    rprint("=" * 100)
    return


@app.command()
def delete_build_triggers(
    project_id: Annotated[
        str, typer.Argument(help="GCP Project ID to create Build job in.")
    ] = DEFAULT_GCP_PROJECT,
    build_trigger: Annotated[
        str,
        typer.Argument(
            help="Specific Build Trigger configuration file to create/update. Use 'all' to create/update all trigger files."
        ),
    ] = "all",
):
    """Update one or all Build Trigger configs
    NOTE: Will DELETE any build triggers defined in the cloudbuild directory ending in "_trigger.yaml"
    """

    triggers_to_delete = []
    if build_trigger == "all":
        triggers_to_delete = glob("./cloudbuild/*_trigger.yaml")
    else:
        triggers_to_delete = [build_trigger]

    delete = typer.confirm(
        "[yellow]:warning: Proceed with deleting build triggers below?{}[/yellow]".format(
            "\n".join(triggers_to_delete)
        )
    )
    if not delete:
        rprint("[yellow]Aborted deleting Cloud Build triggers.[/yellow]")
        raise typer.Abort()

    for trigger_file in triggers_to_delete:
        with open(trigger_file, "r") as f:
            trigger_data = yaml.load(f)
            trigger_name = trigger_data["name"]

        delete_command = [
            "gcloud",
            "triggers",
            "delete",
            f"{trigger_name}",
            f"project={project_id}",
        ]
        delete_resp = subprocess.run(
            args=delete_command,
            check=False,
        )

        if delete_resp.returncode != 0:
            rprint(
                f"[bold red]Failed to delete Build Trigger with configuration at: {build_trigger}[/bold red]"
            )

    rprint("=" * 100)
    rprint("[green]Finished deleting Cloud Build Triggers! :cross_mark:")
    rprint("=" * 100)
    return


if __name__ == "__main__":
    app()
