from src.app import app
from src.util import logger
from src.response import Response


@app.route("/health")
def health_check():
    logger.info("health_check service called")
    res = Response()
    return res()
