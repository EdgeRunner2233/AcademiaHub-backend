import re


def get_logger():
    _logger = None

    def _get_singleton():
        nonlocal _logger
        if _logger is None:
            import logging
            import logging.config
            from pathlib import Path

            ini_path = Path(__file__).absolute().parent.parent / "logging.ini"
            logging.config.fileConfig(ini_path.as_posix())
            _logger = logging.getLogger("infoLogger")
        return _logger

    return _get_singleton()


logger = get_logger()


def check_email_pattern(email: str) -> bool:
    """
    Check if email is valid.

    Args:
        email (str): Email to be checked.

    Returns:
        bool: True if email is valid, False otherwise.
    """

    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None
