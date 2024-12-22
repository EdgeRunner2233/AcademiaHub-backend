import json
import src.util as util
import src.config as config
from src.util import logger
from src.oss import obs_client
from src.response import Response
from src.cache import EmailMessage
from flask import Blueprint, request
from src.api_request import ApiRequest
from src.pre_check import require_fields
from src.model import (
    User,
    PlatformMessages,
    ResearcherApplication,
    Researcher,
    MissingWork,
)

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
    return res(300, data={"id": user.id, "token": token, "info": user.info()})


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
    return res(310, data={"id": user.id, "token": token, "info": user.info()})


@user_service_bp.route("/info", methods=["POST"])
@require_fields("user_id")
def get_user_info():
    req = request.form
    res = Response()

    user_id = req.get("user_id")

    user = User.get_by_id(user_id)
    if not user:
        return res(302)

    return res(0, data=user.info())


@user_service_bp.route("/send_message", methods=["POST"])
@require_fields("sender", "title", "body", "receiver_role")
def send_message():
    req = request.form
    res = Response()

    sender = req.get("sender")
    title = req.get("title")
    body = req.get("body")
    receiver_role = req.get("receiver_role")
    if receiver_role not in ["user", "researcher", "all"]:
        return res(103, "receiver_role")

    if receiver_role == "user" or receiver_role == "all":
        PlatformMessages.create(title, sender, User.Role.USER, body)
    if receiver_role == "researcher" or receiver_role == "all":
        PlatformMessages.create(title, sender, User.Role.RESEARCHER, body)

    return res(0)


@user_service_bp.route("/get_information", methods=["POST"])
@require_fields("id")
def get_message_list():
    req = request.form
    res = Response()

    user_id = req.get("id")

    user = User.get_by_id(user_id)
    if not user:
        return res(302)

    return res(0, data={"messages": PlatformMessages.get_by_receiver(user.role)})


@user_service_bp.route("/change_email", methods=["POST"])
@require_fields("id", "new_email")
def change_email():
    req = request.form
    res = Response()

    user_id = req.get("id")
    new_email = req.get("new_email")

    user = User.get_by_id(user_id)
    if not user:
        return res(302)

    if not util.check_email_pattern(new_email):
        return res(102, "new_email")

    if new_email == user.email:
        return res(322)

    if User.exists(new_email):
        return res(321)

    user.update(email=new_email)
    EmailMessage.send_change_email_success(new_email)

    return res(0)


@user_service_bp.route("/change_password", methods=["POST"])
@require_fields("id", "password", "new_password")
def change_password():
    req = request.form
    res = Response()

    user_id = req.get("id")
    password = req.get("password")
    new_password = req.get("new_password")

    user = User.get_by_id(user_id)
    if not user:
        return res(302)

    if not User.login_check(user.email, password):
        return res(305)

    user.update(password_hash=User.generate_password_hash(new_password))
    EmailMessage.send_change_password_success(user.email)

    return res(0)


@user_service_bp.route("/forget_password", methods=["POST"])
@require_fields("email", "verification_code", "new_password")
def forget_password():
    req = request.form
    res = Response()

    email = req.get("email")
    verification_code = req.get("verification_code")
    new_password = req.get("new_password")

    user = User.get_by_email(email)
    if not user:
        return res(302)

    if not EmailMessage.verify_vcode(email, verification_code):
        return res(304)

    user.update(password_hash=User.generate_password_hash(new_password))
    EmailMessage.send_change_password_success(email)

    return res(0)


@user_service_bp.route("/become_researcher", methods=["POST"])
@require_fields(
    "user_id",
    "work_id",
    "name",
    "gender",
    "birth_date",
    "phone_number",
    "email",
    "address",
    "academic",
    "graduated_school",
    type="form",
)
@require_fields("certificate", "img1", "img2", "achievement", "avatar", type="files")
def become_researcher():
    form = request.form
    files = request.files
    res = Response()

    user_id = form.get("user_id")
    work_id = form.get("work_id")

    real_name = form.get("name")
    gender = form.get("gender")
    birth_date = form.get("birth_date")
    phone_number = form.get("phone_number")
    researcher_email = form.get("email")
    address = form.get("address")
    academic_background = form.get("academic")
    graduated_from = form.get("graduated_school")

    certificate = files.get("certificate")
    id_card_front = files.get("img1")
    id_card_back = files.get("img2")
    academic_achievement = files.get("achievement")
    avatar = files.get("avatar")

    openalex_id = ""

    user = User.get_by_id(user_id)
    if not user:
        return res(302)

    try:
        result = ApiRequest.request_api(f"{config.OPENALEX_BASE}/works/{work_id}")
    except ApiRequest.RequestNotFoundError:
        return res(504)
    except ApiRequest.RequestError:
        return res(502)

    result = json.loads(result)
    authors: list[dict] = result.get("authorships", [])
    for author in authors:
        author_obj = author.get("author", {})
        if author_obj.get("display_name", "") == real_name:
            openalex_id = author_obj.get("id", "").split("/")[-1]
            break

    if openalex_id is None or len(openalex_id) <= 0:
        return res(505)

    if not util.check_email_pattern(researcher_email):
        return res(102, "email")

    try:
        certificate_url = obs_client.put_file(
            certificate.stream.read(),
            f"{util.generate_random_string(20)}/{certificate.filename}",
            config.OBS_APPLICATION_PREFIX,
        )
        id_card_front_url = obs_client.put_file(
            id_card_front.stream.read(),
            f"{util.generate_random_string(20)}/{id_card_front.filename}",
            config.OBS_APPLICATION_PREFIX,
        )
        id_card_back_url = obs_client.put_file(
            id_card_back.stream.read(),
            f"{util.generate_random_string(20)}/{id_card_back.filename}",
            config.OBS_APPLICATION_PREFIX,
        )
        academic_achievement_url = obs_client.put_file(
            academic_achievement.stream.read(),
            f"{util.generate_random_string(20)}/{academic_achievement.filename}",
            config.OBS_APPLICATION_PREFIX,
        )
        avatar_url = obs_client.put_file(
            avatar.stream.read(),
            f"{user_id}/{avatar.filename}",
            config.OBS_AVATAR_PREFIX,
        )
    except obs_client.ObsOperationError:
        return res(503)

    application = ResearcherApplication.create(
        user_id=user_id,
        certificate=certificate_url,
        id_card_front=id_card_front_url,
        id_card_back=id_card_back_url,
        academic_achievement=academic_achievement_url,
    )
    researcher = Researcher.create(
        user_id=user_id,
        openalex_id=openalex_id,
        real_name=real_name,
        gender=gender,
        birth_date=birth_date,
        phone_number=phone_number,
        researcher_email=researcher_email,
        address=address,
        academic_background=academic_background,
        graduated_from=graduated_from,
    )
    if not application or not researcher or not user.update(avatar_url=avatar_url):
        return res(506)

    return res(510)


@user_service_bp.route("/feedback_missing_work", methods=["POST"])
@require_fields("content")
def feedback_missing_work():
    form = request.form
    res = Response()

    content = form.get("content")

    missing_work = MissingWork.create(content)
    if not missing_work:
        return res(506)

    return res(0)
