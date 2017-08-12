from os import path

# App details
BASE_DIRECTORY = path.abspath(path.dirname(__file__))
DEBUG = False
TESTING = False
SECRET_KEY = '\xd3\xc4P\xa5\r{\xdfLr\x04\xb0W\x8bI\x0e`KO\x9b\xfc9\te\x91'

# Database details
db_uri = 'mysql://localhost/bestsocialbuddy'
SQLALCHEMY_DATABASE_URI = db_uri

# Facebook
FB_APP_ID = 'myid'
FB_APP_NAME = 'social-companion'
FB_APP_SECRET = 'mysecret'
