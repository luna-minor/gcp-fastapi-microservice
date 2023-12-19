"""
Cookiecutter Post project generation scripts to clean up and finalize files and directories.
Note: Runs from the directory root of the generated project
"""

import logging
import os
import shutil
import subprocess
import sys


def init_git_repo() -> str:
    """
    Initialize project repo as a git repo (if not already in a git repo)
    :return: Path of git repo root directory
    """

    is_git_repo_resp = subprocess.run(
        args=["git", "rev-parse", "--is-inside-work-tree"]
    )

    # git rev-parse failed, dir is not a git repo, run git init
    if is_git_repo_resp.returncode != 0:
        git_init_output = subprocess.run(args=["git", "init"])
        assert (
            git_init_output.returncode == 0
        ), f"Failed to run git init - stdout: {git_init_output.stdout}; stderr: {git_init_output.stderr}"

    # Return root of git repo
    git_root_resp = subprocess.run(
        args=["git", "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE
    )
    git_root_dir = git_root_resp.stdout.decode("utf-8").strip()

    return git_root_dir


def update_cloud_build_config(git_repo_root: str):
    """
    Update rendered CloudBuild configuration file
    :param git_repo_root: Directory path of project's Git Repository root
    """

    cicd_selection = "{{ cookiecutter.cicd }}"
    if not cicd_selection == "cloudbuild":
        # Cloud Build CICD option not selected, remove directory
        cloudbuild_dir = os.path.join(os.curdir, "cloudbuild")
        # if os.path.exists(cloudbuild_dir) and os.path.isdir(cloudbuild_dir):
        shutil.rmtree(cloudbuild_dir)
        return

    # If generated in a mono-repo, Cloud Build must specify the working directory per setp,
    # then doing a simple find-and-replace here.

    cloudbuild_files = [
        "cloudbuild/cloudbuild.yaml",
        "cloudbuild/pr_main_trigger.yaml",
        "cloudbuild/push_main_trigger.yaml",
    ]
    git_root_placeholder = "TEMP_PLACEHOLDER_GIT_ROOT"
    cloudbuild_dir_placeholder = "TEMP_PLACEHOLDER_BUILD_DIR"
    cloudbuild_include_filter_placeholder = "TEMP_PLACEHOLDER_INCLUDE_FILES"

    project_dir = os.path.abspath(os.curdir)

    # Replace the placeholder string with correct directory for Cloud Build to run steps in

    if project_dir == git_repo_root:
        git_root_placeholder = "."
        cloudbuild_dir = "."
        cloudbuild_include_filter = "**"
        cloudbuild_repo = os.path.basename(
            os.path.normpath(git_repo_root)
        )  # Gets last part of path
    else:
        common_root = os.path.commonprefix([git_repo_root, project_dir])
        relative_project_path = os.path.relpath(project_dir, common_root)
        cloudbuild_dir = f"./{relative_project_path}"
        cloudbuild_include_filter = f"{relative_project_path}/**"
        cloudbuild_repo = os.path.basename(os.path.normpath(common_root))

    # Replace placeholder values in cloudbuild files

    for cb_file in cloudbuild_files:
        with open(cb_file, "r") as file:
            file_text = file.read()
            file_text = (
                file_text.replace(git_root_placeholder, cloudbuild_repo)
                .replace(
                    cloudbuild_include_filter_placeholder, cloudbuild_include_filter
                )
                .replace(cloudbuild_dir_placeholder, cloudbuild_dir)
            )

        with open(cb_file, "w") as file:
            file.write(file_text)

    logging.info("Updated Cloud Build files")
    return


def main_post_project_gen():
    git_root = init_git_repo()

    update_cloud_build_config(git_repo_root=git_root)

    logging.info("Post Project Generation Scripts done!")

    return


if __name__ == "__main__":
    try:
        main_post_project_gen()
    except Exception as e:
        sys.exit(f"{type(e).__name__} - {e}")
