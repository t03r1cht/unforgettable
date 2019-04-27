from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
import locale

# To run in debug:
# Windows: $env:FLASK_DEBUG=1; $env:FLASK_APP="unforgettable.py"; .\venv\Scripts\python.exe -m flask run --port 6913
# Linux:  venv\Scripts\python.exe -m flask run --port 6913

# TODO Python Compiler
# https://nuitka.net/


app = Flask(__name__)
app.config.from_object(Config)
app.logger.setLevel(logging.DEBUG)
app.logger.debug("Starting Flask Web Application...")
logging.basicConfig(filename="unforgettable.log", level=logging.DEBUG)
db = SQLAlchemy(app)
locale.setlocale(locale.LC_ALL, "German")
migrate = Migrate(app, db)
login = LoginManager(app)

from app import routes, models

