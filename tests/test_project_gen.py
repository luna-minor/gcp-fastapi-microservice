import logging
import os
import tempfile
import subprocess
from typing import Optional

import pytest
from cookiecutter.main import cookiecutter


logging.basicConfig(level="INFO")


@pytest.fixture(scope="module")
def temp_output_dir() -> str:
    """ Create a temp directory to generate projects in for testing """
    temp_dir = tempfile.mkdtemp()
    logging.info(f"Created temp dir: {temp_dir}")
    return temp_dir


TEST_CONFIGS = [
    {
        "project_name": "Hello Test1",
        "project_slug": "hello_test1",
        "project_description": "Test Project",
    },
]


def gen_project(output_dir: str, template_values: dict) -> str:
    """Use local cookiecutter template to generate project from config file.
    :param output_dir: Directory to generate project in
    :param template_values: template values to generate project with
    :return: Ccookiecutter output of the generated project directory.
    """

    logging.info(f"Generating example project for project_slug={template_values['project_slug']}")

    # Build cookiecutter project
    resp: str = cookiecutter(
        template=os.getcwd(),
        output_dir=output_dir,
        overwrite_if_exists=True,
        no_input=True,
        extra_context=template_values,
    )
    logging.info(f"Cookiecutter created directory {resp}")

    return resp


def run_script(root_dir: str, command: str, script_path: str, args: Optional[list] = None) -> subprocess.CompletedProcess:
    """Run a script in a subprocess

    Args:
        root_dir (str): Directory to use as root of subprocess
        command (str): Command to run (eg. 'bash', 'python', etc.)
        script_path (str): Path the script to run.
        args (Optional[list], optional): Additional arguments and flags to pass to script. Defaults to None.

    Returns:
        subprocess.CompletedProcess: Completed subprocess response object.
    """
    inital_wdir = os.getcwd()

    os.chdir(root_dir)

    command_args = [command, script_path]

    if args:
        command_args.append(args)

    logging.info(f"Running {command_args}")

    try:
        resp = subprocess.run(
            args=command_args,
            cwd=root_dir,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    finally:
        os.chdir(inital_wdir)
    
    return resp



@pytest.mark.parametrize("template_values", TEST_CONFIGS)
def test_project_gen(template_values: dict, temp_output_dir):
    """Test project generation given a set of template values.
    Test project is generated at expected output dir,
    Test generated project's test pass by running test command in a subprocess.

    Args:
        template_values (dict): Cookiecutter template values to use in project generation.
        temp_output_dir (_type_): A temp directory to generate projects in. Will be removed at test completion.
    """

    generated_project_dir = gen_project(output_dir=temp_output_dir, template_values=template_values)

    # Assert project dir exists
    assert os.path.isdir(generated_project_dir), f"Project not found at {generated_project_dir}"

    # Assert folder name matches project slug
    project_folder = os.path.basename(generated_project_dir)
    assert project_folder == template_values["project_slug"], f"Generated project dir `{project_folder}` differs from exptect of `{template_values['project_slug']}`"


    # Run test scripts in sub-process, assert they pass
    tests_resp = run_script(root_dir=generated_project_dir, command="python", script_path="cli/main.py", args="test")

    if tests_resp.returncode != 0:
        raise Exception(
            f"Failed to pass tests in generated project with values={template_values}\nstdout:{tests_resp.stdout.decode('utf-8')}"
        )

    return
