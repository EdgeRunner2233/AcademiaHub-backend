import json
from src.util import logger
from src.response import Response
from flask import Blueprint, request
from src.api_request import request_api

rsc_service_bp = Blueprint("rsc_service", __name__, url_prefix="/api/researcher")

OPENALEX_BASE = "https://api.openalex.org/"


@rsc_service_bp.route("/health", methods=["GET", "POST"])
def health_check():
    logger.info("health_check of researcher service called")
    res = Response()
    return res(0)


@rsc_service_bp.route("/info", methods=["POST"])
def get_info():
    logger.info("get_info of researcher service called")
    req = request.form
    res = Response()

    researcher_id = req.get("researcher_id", None)
    if not researcher_id:
        return res(101, "researcher_id")

    code, result = request_api(f"{OPENALEX_BASE}/authors/{researcher_id}")

    if code == 404:
        return res(501)
    elif code != 200:
        return res(502)

    result = json.loads(result)
    data = {
        "openalex_id": result.get("id").replace("https://openalex.org/", ""),
        "orcid": result.get("orcid").replace("https://orcid.org/", ""),
        "name": result.get("display_name"),
        "works_count": result.get("works_count"),
        "cited_by_count": result.get("cited_by_count"),
        "summary_stats": result.get("summary_stats"),
    }
    return res(0, data=data)
