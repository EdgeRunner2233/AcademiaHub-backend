from flask import Blueprint
from src.model import User
from src.util import logger
from src.response import Response

service_bp = Blueprint("service", __name__)


@service_bp.route("/api/health")
def health_check():
    logger.info("health_check service called")
    res = Response()
    return res()
