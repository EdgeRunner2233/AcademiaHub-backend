import functools
from flask import request
from src.model import User
from src.response import Response


def permission(required_role=User.Role.USER, field="id", type="form"):
    """
    Decorator to check if user has permission to access the endpoint.

    Args:
        required_role (int, optional): Required role. Defaults to USER.
        field (str, optional): Field to check. Defaults to "id".
        type (str, optional): Type of request data. Defaults to "form".
    """

    def decorator(f):
        @functools.wraps(f)
        def warper(*args, **kwargs):
            res = Response()
            if type == "form":
                field_value = request.form.get(field, None)
            elif type == "json":
                field_value = request.json.get(field, None)
            elif type == "args":
                field_value = request.args.get(field, None)
            else:
                return res(999)
            user = User.query_first(**{field: field_value})
            if not user:
                return res(302)
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
                    or (type == "files" and field not in request.files)
                ):
                    res = Response()
                    return res(101, field)
            return f(*args, **kwargs)

        return warper

    return decorator
