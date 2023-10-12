import os

from cookiecutter.main import cookiecutter

example_configs = [
    x
    for x in os.listdir("examples")
    if x.endswith(".yaml") and os.path.isfile(os.path.join("examples", x))
]

for example_config in example_configs:
    resp = cookiecutter(
        template=os.getcwd(),
        output_dir="./examples",
        overwrite_if_exists=True,
        no_input=True,
        config_file=os.path.join("examples", example_config),
    )
    print(f"Cookiecutter created directory {resp}")
