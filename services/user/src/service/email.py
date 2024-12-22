import src.util as util
from src.model import User
from src.response import Response
from src.cache import EmailMessage
from flask import Blueprint, request
from src.pre_check import require_fields

email_service_bp = Blueprint("email_service", __name__, url_prefix="/api/email")


@email_service_bp.route("/send", methods=["POST"])
@require_fields("recipient", "subject", "body")
def send_email():
    form = request.form
    res = Response()

    recipient = form.get("recipient")
    subject = form.get("subject")
    body = form.get("body")

    user = User.get_by_id(recipient)
    if not user:
        return res(302)

    if not util.check_email_pattern(user.email):
        return res(102, "user's email")

    EmailMessage.send(user.email, subject, body)

    return res(0)
