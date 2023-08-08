import typer

app = typer.Typer(
    name="TEMP_CLI",
    no_args_is_help=True,
)


@app.command()
def start_local_server():
    """Start serivce on localhost"""
    return


@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")


if __name__ == "__main__":
    app()
