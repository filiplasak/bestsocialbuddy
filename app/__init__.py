from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object('app.default_config')
app.config.from_envvar('FLASK_CONFIG_PATH', silent=True)

print(app.config)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

from app import views, models
