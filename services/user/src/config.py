from pathlib import Path

__version__ = "v0.0.7"


OPENALEX_BASE = "https://api.openalex.org/"
INI_PATH = Path(__file__).absolute().parent.parent / "logging.ini"


def version():
    return __version__
