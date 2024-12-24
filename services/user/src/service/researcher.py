import json
from src.util import logger
import src.config as config
from src.response import Response
from flask import Blueprint, request
from src.api_request import ApiRequest
from src.model import User, Researcher
from src.pre_check import require_fields
from src.cache import CachedWork, CachedAuthor

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
        result = CachedAuthor.get(researcher_id)
    except CachedAuthor.CacheNotFound:
        try:
            result = ApiRequest.request_api(
                f"{config.OPENALEX_BASE}/authors/{researcher_id}"
            )
            result: dict = json.loads(result)  # type: ignore
            CachedAuthor.set(researcher_id, result)
        except ApiRequest.RequestNotFoundError:
            return res(501)
        except ApiRequest.RequestError:
            return res(502)

    researcher = Researcher.query_first(openalex_id=researcher_id)
    user = User.get_by_id(researcher.user_id) if researcher else None

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
        "email": researcher.researcher_email if researcher else "",
        "topics": list(set(domains)),
        "institution": {
            "name": institution.get("display_name", ""),
            "id": institution.get("id", ""),
        },
    }

    work_id = result.get("works_api_url")
    try:
        works = CachedWork.get(work_id)
    except CachedWork.CacheNotFound:
        try:
            works = ApiRequest.request_api(result.get("works_api_url"))
            works: list[dict] = json.loads(works).get("results", [])  # type: ignore
            CachedWork.set(work_id, works)
        except ApiRequest.RequestError:
            return res(502)

    coauthors = []
    coauthor_ids = []
    for work in works:
        for author in work.get("authorships", []):
            cooperator: dict = author.get("author")
            cid = cooperator.get("id", "").split("/")[-1]
            if cid == researcher_id:
                continue
            if cid not in coauthor_ids:
                coauthors.append(
                    {
                        "name": cooperator.get("display_name", ""),
                        "id": cid,
                        "coauthor_times": 1,
                    }
                )
            else:
                for coauthor in coauthors:
                    if coauthor.get("id", None) == cid:
                        coauthor["coauthor_times"] += 1
            coauthor_ids.append(cid)

    coauthors.sort(key=lambda x: x["coauthor_times"], reverse=True)
    data["cooperators"] = coauthors[:10]
    data["works"] = [
        {
            "title": x.get("title", ""),
            "publication_date": x.get("publication_date", ""),
            "id": x.get("id", ""),
        }
        for x in works
    ]

    return res(0, data=data)


@rsc_service_bp.route("/coauthor", methods=["POST"])
@require_fields("researcher_id")
def get_coauthor():
    logger.info("get_coauthor of researcher service called")
    req = request.form
    res = Response()

    researcher_id = req.get("researcher_id", "")

    try:
        result = CachedAuthor.get(researcher_id)
    except CachedAuthor.CacheNotFound:
        try:
            result = ApiRequest.request_api(
                f"{config.OPENALEX_BASE}/authors/{researcher_id}"
            )
            result: dict = json.loads(result)  # type: ignore
            CachedAuthor.set(researcher_id, result)
        except ApiRequest.RequestNotFoundError:
            return res(501)
        except ApiRequest.RequestError:
            return res(502)

    work_id = result.get("works_api_url")
    try:
        works = CachedWork.get(work_id)
    except CachedWork.CacheNotFound:
        try:
            works = ApiRequest.request_api(result.get("works_api_url"))
            works: list[dict] = json.loads(works).get("results", [])  # type: ignore
            CachedWork.set(work_id, works)
        except ApiRequest.RequestError:
            return res(502)

    coauthors = []
    coauthor_ids = []
    for work in works:
        for author in work.get("authorships", []):
            cooperator: dict = author.get("author")
            cid = cooperator.get("id", "").split("/")[-1]
            if cid == researcher_id:
                continue
            if cid not in coauthor_ids:
                coauthors.append(
                    {
                        "name": cooperator.get("display_name", ""),
                        "id": cid,
                        "coauthor_times": 1,
                    }
                )
            else:
                for coauthor in coauthors:
                    if coauthor.get("id", None) == cid:
                        coauthor["coauthor_times"] += 1
            coauthor_ids.append(cid)

    coauthors.sort(key=lambda x: x["coauthor_times"], reverse=True)
    coauthors = coauthors[:10]

    return res(0, data={"coauthors": coauthors})
