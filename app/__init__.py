from flask import Flask
import os

# UPLOAD_FOLDER = 'C:\\Users\\jessf\\Documents\\flask\\microblog\\app\\uploads'
# UPLOAD_FOLDER = 'C:\\Users\\Saul\\Documents\\Saúl documentos\\CUCEI\\9no Semestre\\Mineria_datos\\Proyecto_final\\Repof\\app\\uploads'
UPLOAD_FOLDER = 'C:\\Users\\leonc\\Documents\\CUCEI\\9no_semestre\\Minería_de_datos\\ProyectoFinal\\Repof\\app\\uploads'

# ROOT_FOLDER = os.getcwd()
# print(ROOT_FOLDER)
# UPLOAD_FOLDER = '\\uploads\\'
# DATA_FOLDER = '\\data\\'
# HOME_ROUTE = '/home'
# FILES = [ 'data.csv', 'properties.json' ]

# app = Flask(__name__)
# app.config['ROOT_FOLDER'] = ROOT_FOLDER
# app.secret_key = "secret key"
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['DATA_FOLDER'] = DATA_FOLDER
# app.config['HOME_ROUTE'] = HOME_ROUTE
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
# app.config['FILES'] = FILES

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

from app.views import routes