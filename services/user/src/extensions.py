from flask_mail import Mail
from flask_babel import Babel
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy


mail = Mail()
babel = Babel()
db = SQLAlchemy()
redis = FlaskRedis()
