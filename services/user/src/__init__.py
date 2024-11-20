import os
from flask import Flask
from src.extensions import babel, db
from src.service import service_bp
from dotenv import load_dotenv

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

    db.init_app(app)
    babel.init_app(app)

    app.register_blueprint(service_bp)

    return app
