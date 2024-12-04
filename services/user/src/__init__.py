import os
from flask import Flask
from dotenv import load_dotenv
from src.service import service_bp
from src.extensions import babel, db, mail

load_dotenv()


def create_app(**config):
    app = Flask(__name__)

    if config:
        app.config.from_mapping(**config)
    else:
        app.config.from_mapping(
            SECRET_KEY=os.getenv("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.getenv("SQLALCHEMY_DATABASE_URI"),
        )

    app.config.update(
        MAIL_SERVER=os.getenv("MAIL_SERVER"),
        MAIL_PORT=os.getenv("MAIL_PORT"),
        MAIL_USE_SSL=os.getenv("MAIL_USE_SSL"),
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER"),
    )

    db.init_app(app)
    mail.init_app(app)
    babel.init_app(app)

    app.register_blueprint(service_bp)

    return app
