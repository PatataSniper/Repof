from flask import Flask

# UPLOAD_FOLDER = 'C:\\Users\\jessf\\Documents\\flask\\microblog\\app\\uploads'
UPLOAD_FOLDER = 'C:\\Users\\Saul\\Documents\\Saúl documentos\\CUCEI\\9no Semestre\\Mineria_datos\\Proyecto_final\\Repof\\app\\uploads'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

from app.views import routes