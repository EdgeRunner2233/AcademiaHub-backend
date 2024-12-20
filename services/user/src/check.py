import functools
from flask import request
from src.model import User
from src.response import Response


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
