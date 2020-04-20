from flask import Flask

UPLOAD_FOLDER = 'C:\\Users\\jessf\\Documents\\flask\\microblog\\app\\uploads'
HOME_ROUTE = '/home'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['HOME_ROUTE'] = HOME_ROUTE
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
