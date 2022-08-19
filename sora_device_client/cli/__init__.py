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


app.command()(login.login)
app.command()(logout.logout)
app.command()(start.start)
