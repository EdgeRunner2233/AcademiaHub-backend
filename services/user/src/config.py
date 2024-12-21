import os
from pathlib import Path

__version__ = "v0.0.8"


OPENALEX_BASE = "https://api.openalex.org/"
INI_PATH = Path(__file__).absolute().parent.parent / "logging.ini"


OBS_AK = os.getenv("OBS_ACCESS_KEY")
OBS_SK = os.getenv("OBS_SECRET_KEY")
OBS_SERVER = "obs.cn-north-4.myhuaweicloud.com"
OBS_BUCKET_NAME = "academiahub"
OBS_BASE_URL = "https://academiahub.obs.cn-north-4.myhuaweicloud.com/"
OBS_AVATAR_PREFIX = "user/avatar/"


DEFAULT_AVATAR_URL = OBS_BASE_URL + "user/avatar/default.png"


DB_DELIMITER = "$|$"


def version():
    return __version__
