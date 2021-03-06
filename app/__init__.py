from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cache import Cache
from flask.logging import getLogger, DEBUG

app = Flask(__name__)
app.config.from_object('app.default_config')
app.config.from_envvar('FLASK_CONFIG_PATH', silent=True)

if app.debug:
    log = getLogger('console')
    log.setLevel(DEBUG)
else:
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('bsb.log')
    file_handler.setLevel(DEBUG)
    app.logger.addHandler(file_handler)

app.logger.debug(app.config)

cache = Cache(app, config=app.config)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

from app import views, models
