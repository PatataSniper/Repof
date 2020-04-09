from app import app
from flask import session, redirect

from app.views.upload import *
from app.views.download import *

HOME_ROUTE = app.config['HOME_ROUTE']

@app.route('/')
def __init__():
    return redirect(HOME_ROUTE)

@app.route('/home')
def home():
    if 'data' in session and 'schema' in session:
        return render_template('home.html', data=session['data'], schema=session['schema'])
    return render_template('home.html')

if __name__ == "__main__":
    app.run()
