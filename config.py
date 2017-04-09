from os import path

# App details
BASE_DIRECTORY = path.abspath(path.dirname(__file__))
DEBUG = True
SECRET_KEY = 'keep_it_like_a_secret'

# Database details
db_path = path.join(BASE_DIRECTORY, 'app.db')
db_uri = 'sqlite:///{}'.format(db_path)
SQLALCHEMY_DATABASE_URI = db_uri

# Facebook
FB_APP_ID = 'myid'
FB_APP_NAME = 'social-companion'
FB_APP_SECRET = 'mysecret'
