import functools
from src.util import logger
from src.model import User
from src.response import Response
from flask import Blueprint, request

service_bp = Blueprint("service", __name__, url_prefix="/api/user")


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


@service_bp.route("/health", methods=["GET", "POST"])
def health_check():
    logger.info("health_check service called")
    res = Response()
    return res(0)


@service_bp.route("/login", methods=["POST"])
def login():
    req: dict = request.json
    res = Response()

    user_email = req.get("email", None)
    user_password = req.get("password", None)

    if not user_email:
        return res(101, "email")
    if not user_password:
        return res(101, "password")

    if not User.login_check(user_email, user_password):
        return res(301)

    user = User.get_by_email(user_email)
    token = user.generate_token()
    return res(300, data={"id": user.id, "token": token})


@service_bp.route("/register", methods=["POST"])
def register():
    req: dict = request.json
    res = Response()

    user_email = req.get("email")
    user_nickname = req.get("nickname")
    user_password = req.get("password")

    if not user_email:
        return res(101, "email")
    if not user_nickname:
        return res(101, "nickname")
    if not user_password:
        return res(101, "password")

    if User.exists(user_email):
        return res(311)

    user = User.create(user_email, user_nickname, user_password)
    if not user:
        return res(319)

    token = user.generate_token()
    return res(310, data={"id": user.id, "token": token})
