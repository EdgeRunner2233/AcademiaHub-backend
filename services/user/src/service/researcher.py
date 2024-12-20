from src.util import logger
from src.response import Response
from flask import Blueprint

rsc_service_bp = Blueprint("rsc_service", __name__, url_prefix="/api/researcher")


@rsc_service_bp.route("/health", methods=["GET", "POST"])
def health_check():
    logger.info("health_check service called")
    res = Response()
    return res(0)
