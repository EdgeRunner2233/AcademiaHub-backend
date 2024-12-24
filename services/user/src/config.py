import os
from pathlib import Path

__version__ = "v1.3.1"


OPENALEX_BASE = "https://api.openalex.org"
INI_PATH = Path(__file__).absolute().parent.parent / "logging.ini"

OBS_AK = os.getenv("OBS_ACCESS_KEY")
OBS_SK = os.getenv("OBS_SECRET_KEY")
OBS_SERVER = "obs.cn-north-4.myhuaweicloud.com"
OBS_BUCKET_NAME = "academiahub"
OBS_BASE_URL = "https://academiahub.obs.cn-north-4.myhuaweicloud.com/"
OBS_AVATAR_PREFIX = "user/avatar/"
OBS_APPLICATION_PREFIX = "user/application/"

DEFAULT_AVATAR_URL = OBS_BASE_URL + "user/avatar/default.png"

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8"
DB_DELIMITER = "$|$"

INFO_CACHE_EXPIRE_TIME = 36000


def version():
    return __version__
