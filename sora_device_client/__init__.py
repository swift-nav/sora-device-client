import importlib.metadata

if not __package__:
    __version__ = "(local)"
else:
    __version__ = importlib.metadata.version(__package__)
