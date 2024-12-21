import src.util as util
from src.model import User
import src.config as config
from src.util import logger
from src.cache import EmailMessage
from src.response import Response
from flask import Blueprint, request
from src.pre_check import require_fields

user_service_bp = Blueprint("usr_service", __name__, url_prefix="/api/user")


@user_service_bp.route("/health", methods=["GET", "POST"])
def health_check():
    logger.info("health_check service called")
    res = Response()
    return res(0, data={"version": config.version()})


@user_service_bp.route("/get_verification", methods=["POST"])
@require_fields("email")
def send_verification():
    req = request.form
    res = Response()

    user_email = req.get("email", None)
    if not util.check_email_pattern(user_email):
        return res(102, "email")

    EmailMessage.send_vcode(user_email)

    return res(0)


@user_service_bp.route("/login", methods=["POST"])
@require_fields("email", "password")
def login():
    req = request.form
    res = Response()

    user_email = req.get("email", None)
    user_password = req.get("password", None)

    if not User.login_check(user_email, user_password):
        return res(301)

    user = User.get_by_email(user_email)
    token = user.generate_token()
    return res(300, data={"id": user.id, "token": token})


@user_service_bp.route("/register", methods=["POST"])
@require_fields("email", "nickname", "password", "verification_code")
def register():
    req = request.form
    res = Response()

    user_email = req.get("email")
    user_nickname = req.get("nickname")
    user_password = req.get("password")
    verification_code = req.get("verification_code")

    if User.exists(user_email):
        return res(311)

    if not EmailMessage.verify_vcode(user_email, verification_code):
        return res(304)

    EmailMessage.send_register_success(user_email)

    user = User.create(user_email, user_nickname, user_password)

    token = user.generate_token()
    return res(310, data={"id": user.id, "token": token})


@user_service_bp.route("/info", methods=["POST"])
@require_fields("email")
def get_user_info():
    req = request.form
    res = Response()

    email = req.get("email")

    user = User.get_by_email(email)
    if not user:
        return res(302)

    return res(0, data=user.info())


@user_service_bp.route("/change_email", methods=["POST"])
@require_fields("email", "new_email")
def change_email():
    req = request.form
    res = Response()

    user_email = req.get("email")
    new_email = req.get("new_email")

    user = User.get_by_email(user_email)
    if not user:
        return res(302)

    if not util.check_email_pattern(new_email):
        return res(102, "new_email")

    if new_email == user_email:
        return res(322)

    if User.exists(new_email):
        return res(321)

    user.update(email=new_email)
    EmailMessage.send_change_email_success(new_email)

    return res(0)


@user_service_bp.route("/change_password", methods=["POST"])
@require_fields("email", "password", "new_password")
def change_password():
    req = request.form
    res = Response()

    email = req.get("email")
    password = req.get("password")
    new_password = req.get("new_password")

    user = User.get_by_email(email)
    if not user:
        return res(302)

    if not User.login_check(email, password):
        return res(305)

    user.update(password_hash=User.generate_password_hash(new_password))
    EmailMessage.send_change_password_success(email)

    return res(0)
