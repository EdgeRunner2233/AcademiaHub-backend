import json
from src.model import User
from src.util import logger
import src.config as config
from src.response import Response
from flask import Blueprint, request
from src.api_request import ApiRequest
from src.pre_check import require_fields

rsc_service_bp = Blueprint("rsc_service", __name__, url_prefix="/api/researcher")


@rsc_service_bp.route("/health", methods=["GET", "POST"])
def health_check():
    logger.info("health_check of researcher service called")
    res = Response()
    return res(0, data={"version": config.version()})


@rsc_service_bp.route("/info", methods=["POST"])
@require_fields("researcher_id")
def get_info():
    logger.info("get_info of researcher service called")
    req = request.form
    res = Response()

    researcher_id = req.get("researcher_id", "")

    try:
        result = ApiRequest.request_api(
            f"{config.OPENALEX_BASE}/authors/{researcher_id}"
        )
    except ApiRequest.RequestNotFoundError:
        return res(501)
    except ApiRequest.RequestError:
        return res(502)

    user = User.query_first(openalex_id=researcher_id)

    result: dict = json.loads(result)  # type: ignore
    domains = [
        x.get("domain", {}).get("display_name", "")
        for x in result.get("topics", [])
        if x
    ]
    institution: dict = result.get("last_known_institutions", [{}])[0]  # type: ignore
    data = {
        "openalex_id": result.get("id", ""),
        "orcid": result.get("orcid", ""),
        "name": result.get("display_name", ""),
        "works_count": result.get("works_count", 0),
        "cited_by_count": result.get("cited_by_count", 0),
        "summary_stats": result.get("summary_stats", {}),
        "avatar_url": user.avatar_url if user else config.DEFAULT_AVATAR_URL,
        "email": user.email if user else "",
        "topics": list(set(domains)),
        "institution": {
            "name": institution.get("display_name", ""),
            "id": institution.get("id", ""),
        },
    }

    try:
        works = ApiRequest.request_api(result.get("works_api_url"))
    except ApiRequest.RequestError:
        return res(502)
    works: list[dict] = json.loads(works).get("results", [])  # type: ignore

    data["cooperators"] = []
    for work in works:
        for author in work.get("authorships", []):
            cooperator = author.get("author")
            if cooperator and cooperator not in data["cooperators"]:
                data["cooperators"].append(cooperator)
    data["works"] = [
        {
            "title": x.get("title", ""),
            "publication_date": x.get("publication_date", ""),
            "id": x.get("id", ""),
        }
        for x in works
    ]

    return res(0, data=data)
