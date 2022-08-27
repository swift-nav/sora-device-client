import typer
import tomlkit

from ..exceptions import DataFileNotFound
from ..config import read_data, write_data


def logout():
    """
    Log the device out of Sora Server.
    """
    try:
        data = read_data()
    except DataFileNotFound:
        raise typer.Exit("Device not logged in.")

    try:
        del data["device"]
    except tomlkit.container.NonExistentKey:
        pass

    write_data(data)
