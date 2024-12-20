import re
import functools
from flask import request
from src.model import User
from src.response import Response


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


def permission(required_role=User.Role.USER):
    def decorator(f):
        @functools.wraps(f)
        def warper(*args, **kwargs):
            res = Response()
            token = request.headers.get("Authorization", "")
            if not token:
                return res(401)
            user, err = User.get_by_token(token)
            if err > 0:
                return res(err)
            elif user.role < required_role:
                return res(404)
            else:
                return f(*args, **kwargs)

        return warper

    return decorator


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
