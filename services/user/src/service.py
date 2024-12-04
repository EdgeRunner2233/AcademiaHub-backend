import functools
import src.util as util
from src.model import User
from src.util import logger
from src.response import Response
from flask import Blueprint, request
from src.util import VerificationCode

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


@service_bp.route("/get_verification", methods=["POST"])
def send_verification():
    req = request.form
    res = Response()

    user_email = req.get("email", None)
    if not util.check_email_pattern(user_email):
        return res(102, "email")

    virification_code = VerificationCode.generate_code()
    user = User.get_by_email(user_email)

    if user is None:
        user = User.create(user_email, "", "")

    user.update(pending_verification_code=virification_code)

    VerificationCode.send_verification_code(user_email, virification_code)

    return res(0)


@service_bp.route("/login", methods=["POST"])
def login():
    req = request.form
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
    req = request.form
    res = Response()

    user_email = req.get("email")
    user_nickname = req.get("nickname")
    user_password = req.get("password")
    verification_code = req.get("verification_code")

    if not user_email:
        return res(101, "email")
    if not user_nickname:
        return res(101, "nickname")
    if not user_password:
        return res(101, "password")

    user = User.get_by_email(user_email)
    if user is None:
        return res(303)
    if user.is_activated:
        return res(311)

    if user.pending_verification_code != verification_code:
        return res(304)

    user.update(
        email=user_email,
        nickname=user_nickname,
        password_hash=User.generate_password_hash(user_password),
        pending_verification_code="",
        is_activated=True,
    )

    token = user.generate_token()
    return res(310, data={"id": user.id, "token": token})
