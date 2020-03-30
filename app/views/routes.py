from app import app
from app.views.upload import *
from flask import session

@app.route('/home')
def upload_form():
    if 'data' in session and 'schema' in session:
        return render_template('home.html', data=session['data'], schema=session['schema'])
    return render_template('home.html')

if __name__ == "__main__":
    app.run()
