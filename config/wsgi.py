import os
os.environ['FLASK_CONFIG_PATH'] = '/home/bestsocialbuddy/config_prod.py'

from app import app

if __name__ == '__main__':
    app.run()
