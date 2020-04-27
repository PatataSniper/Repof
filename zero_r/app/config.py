import os
from app import app

APP_FOLDER = os.path.dirname(os.path.realpath(__file__))
DATA_FOLDER = os.path.join(APP_FOLDER, 'data')

app.config['APP_FOLDER'] = APP_FOLDER
app.config['DATA_FOLDER'] = DATA_FOLDER