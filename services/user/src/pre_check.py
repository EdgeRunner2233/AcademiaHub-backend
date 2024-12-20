import functools
from flask import request
from src.model import User
from src.response import Response


def permission(required_role=User.Role.USER):
    """
    Decorator to check if user has permission to access the endpoint.

    Args:
        required_role (int, optional): Required role. Defaults to USER.
    """

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


def require_fields(*fields: str, type="form"):
    """
    Decorator to check if required fields are present in request.

    Args:
        fields (str): List of required fields.
        type (str, optional): Type of request data. Defaults to "form".
    """

    def decorator(f):
        @functools.wraps(f)
        def warper(*args, **kwargs):

            for field in fields:
                if (
                    (type == "form" and field not in request.form)
                    or (type == "json" and field not in request.json)
                    or (type == "args" and field not in request.args)
                ):
                    res = Response()
                    return res(101, field)
            return f(*args, **kwargs)

        return warper

    return decorator
