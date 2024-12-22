from src.response import Response
from flask import Blueprint, request
from src.pre_check import require_fields
from src.model import User, Researcher, ResearcherApplication

admin_service_bp = Blueprint("admin_service", __name__, url_prefix="/api/admin")


@admin_service_bp.route("/get_researcher_applications", methods=["POST"])
@require_fields("user_id")
# @permission(User.Role.ADMIN, "user_id", "form")
def get_pending_researcher_applications():
    res = Response()

    applications = ResearcherApplication.get_all_pending()

    return res(0, data={"applications": applications})


@admin_service_bp.route("/approve_researcher_application", methods=["POST"])
@require_fields("id", "user_id")
# @permission(User.Role.ADMIN, "id", "form")
def approve_researcher_application():
    form = request.form
    res = Response()

    user_id = form.get("user_id")
    application = ResearcherApplication.get_by_user_id(user_id)
    researcher = Researcher.query_first(user_id=user_id, is_valid=False)
    if not application or not researcher:
        return res(511)

    application.delete()
    researcher.update(is_valid=True)

    return res(0)


@admin_service_bp.route("/disapprove_researcher_application", methods=["POST"])
@require_fields("id", "user_id")
# @permission(User.Role.ADMIN, "id", "form")
def disapprove_researcher_application():
    form = request.form
    res = Response()

    user_id = form.get("user_id")
    application = ResearcherApplication.get_by_user_id(user_id)
    researcher = Researcher.query_first(user_id=user_id, is_valid=False)
    if not application or not researcher:
        return res(511)

    application.delete()
    researcher.delete()

    return res(0)


@admin_service_bp.route("/user_num", methods=["GET", "POST"])
def get_user_num():
    res = Response()

    return res(0, data={"user_num": User.count(), "researcher_num": Researcher.count()})
