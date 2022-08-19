import logging
import os
import pathlib
import tomlkit
import typer


from rich.logging import RichHandler

from . import login, logout, start
from ..exceptions import DataFileNotFound

log = logging.getLogger(__name__)
app = typer.Typer()
app.add_typer(login.app, name="login")
app.add_typer(logout.app, name="logout")
app.add_typer(start.app, name="start")


def setup_logger(verbose=False, debug=False):
    logging.basicConfig(
        level=(
            logging.DEBUG if debug else logging.INFO if verbose else logging.WARNING
        ),
        format="%(message)s",
        handlers=[RichHandler()],
    )


@app.callback()
def callback(verbose: bool = False, debug: bool = False):
    """
    Sora Device Client
    """
    setup_logger(verbose, debug)
