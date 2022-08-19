import typer
import tomlkit

from rich import print
from rich.logging import RichHandler

from ..exceptions import DataFileNotFound
from ..config import DATA_FILE_PATH, read_data, write_data

app = typer.Typer()


@app.command()
def logout():
    """
    Log the device out of Sora Server.
    """
    try:
        data = read_data()
    except DataFileNotFound:
        raise typer.Exit("Device not logged in.")

    try:
        del data["device-id"]
    except tomlkit.container.NonExistentKey:
        pass

    write_data(DATA_FILE_PATH, data)
