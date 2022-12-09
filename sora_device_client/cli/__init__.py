import logging
import typer
import sys
from typing import *

from rich.logging import RichHandler

from . import login, logout, start, paths

log = logging.getLogger(__name__)
app = typer.Typer()


def setup_logger(verbose: bool = False, debug: bool = False) -> None:
    logging.basicConfig(
        level=(
            logging.DEBUG if debug else logging.INFO if verbose else logging.WARNING
        ),
        format="%(message)s",
        handlers=[RichHandler()],
    )


def _version(_val: bool) -> None:
    if not _val:
        return
    from .. import __version__

    print(f"Sora device client version: {__version__}", file=sys.stderr)
    raise typer.Exit(0)


@app.callback()
def callback(
    verbose: bool = typer.Option(False, "--verbose"),
    debug: bool = typer.Option(False, "--debug"),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=_version, is_eager=True
    ),
) -> None:
    """
    Sora Device Client

    Streams Location Data from a location source to the Sora Service
    """
    setup_logger(verbose, debug)


app.command()(login.login)
app.command()(logout.logout)
app.command()(start.start)
app.command()(paths.paths)
