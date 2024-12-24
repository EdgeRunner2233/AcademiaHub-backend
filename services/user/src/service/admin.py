from src.response import Response
from src.cache import EmailMessage
from flask import Blueprint, request
from src.pre_check import require_fields
from src.model import User, Researcher, ResearcherApplication, MissingWork

admin_service_bp = Blueprint("admin_service", __name__, url_prefix="/api/admin")


@admin_service_bp.route("/get_researcher_applications", methods=["POST"])
@require_fields("user_id")
# @permission(User.Role.ADMIN, "user_id", "form")
def get_pending_researcher_applications():
    res = Response()

    applications = ResearcherApplication.get_all_pending()
    for application in applications:
        user_id = application.get("user_id", "")
        researcher = Researcher.query_first(user_id=user_id, is_valid=False)
        application.update(researcher.info() if researcher else {})

    return res(0, data={"applications": applications})


@admin_service_bp.route("/approve_researcher_application", methods=["POST"])
@require_fields("id", "user_id")
# @permission(User.Role.ADMIN, "id", "form")
def approve_researcher_application():
    form = request.form
    res = Response()

    user_id = form.get("user_id")

    user = User.get_by_id(user_id)
    if not user:
        return res(302)

    application = ResearcherApplication.get_by_user_id(user_id)
    if not application:
        return res(511)

    application.delete()
    existing_researcher = Researcher.query_first(user_id=user_id, is_valid=True)
    new_researcher = Researcher.query_first(user_id=user_id, is_valid=False)
    if not existing_researcher:
        new_researcher.update(is_valid=True)
        user.update(role=User.Role.RESEARCHER)
        EmailMessage.send_become_researcher(user.email)
    else:
        existing_researcher.delete()
        new_researcher.update(is_valid=True)
        EmailMessage.send_update_researcher_info(user.email)

    return res(0)


@admin_service_bp.route("/disapprove_researcher_application", methods=["POST"])
@require_fields("id", "user_id")
# @permission(User.Role.ADMIN, "id", "form")
def disapprove_researcher_application():
    form = request.form
    res = Response()

    user_id = form.get("user_id")

    user = User.get_by_id(user_id)
    if not user:
        return res(302)

    application = ResearcherApplication.get_by_user_id(user_id)
    researcher = Researcher.query_first(user_id=user_id, is_valid=False)
    if not application or not researcher:
        return res(511)

    application.delete()
    researcher.delete()

    EmailMessage.send_rejected_researcher(user.email)

    return res(0)


@admin_service_bp.route("/user_num", methods=["GET", "POST"])
def get_user_num():
    res = Response()

    return res(
        0,
        data={
            "user_num": User.count(role=User.Role.USER),
            "researcher_num": User.count(role=User.Role.RESEARCHER),
        },
    )


@admin_service_bp.route("/get_unread_feedback", methods=["GET", "POST"])
def all_unread_feedback():
    res = Response()

    return res(0, data={"feedbacks": MissingWork.get_unread()})


@admin_service_bp.route("/read_feedback", methods=["POST"])
@require_fields("id")
def read_feedback():
    form = request.form
    res = Response()

    missing_work_id = form.get("id")
    missing_work = MissingWork.query_first(id=missing_work_id, is_read=False)

    if not missing_work:
        return res(521)

    missing_work.update(is_read=True)

    return res(0)
