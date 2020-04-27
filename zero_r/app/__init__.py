from flask import Flask

app = Flask(__name__)
app.secret_key = "secret key"

from app.config import app
from app.views import routes