import os
from flask import Flask

ROOT_FOLDER = os.getcwd()
print(ROOT_FOLDER)
UPLOAD_FOLDER = '\\uploads\\'
DATA_FOLDER = '\\data\\'
HOME_ROUTE = '/home'
FILES = [ 'data.csv', 'properties.json' ]

app = Flask(__name__)
app.config['ROOT_FOLDER'] = ROOT_FOLDER
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATA_FOLDER'] = DATA_FOLDER
app.config['HOME_ROUTE'] = HOME_ROUTE
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['FILES'] = FILES
