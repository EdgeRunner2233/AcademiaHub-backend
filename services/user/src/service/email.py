import src.util as util
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

    recipient = form.get("recipient").strip()
    subject = form.get("subject")
    body = form.get("body")

    if not util.check_email_pattern(recipient):
        return res(102, "recipient")

    EmailMessage.send(recipient, subject, body)

    return res(0)
