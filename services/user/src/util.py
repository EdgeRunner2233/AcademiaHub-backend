import re
import string
import random
from src.config import INI_PATH


def get_logger():
    _logger = None

    def _get_singleton():
        nonlocal _logger
        if _logger is None:
            import logging
            import logging.config

            logging.config.fileConfig(INI_PATH.as_posix())
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


def generate_random_string(length=5) -> str:
    """
    Generate a random string of given length.

    Args:
        length (int, optional): Length of the random string. Defaults to 5.

    Returns:
        str: Random string.
    """

    return "".join(random.choices(string.ascii_letters + string.digits, k=length))
