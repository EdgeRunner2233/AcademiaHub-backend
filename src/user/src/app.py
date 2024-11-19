from flask import Flask
from flask_babel import Babel
from dotenv import load_dotenv

assert load_dotenv()

app = Flask(__name__)
babel = Babel(app)

import src.model
import src.service
