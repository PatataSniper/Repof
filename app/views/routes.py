import os
import urllib.request
from app import app
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
from app.models.properties import Properties
from app.models.table import Table

ALLOWED_EXTENSIONS = set(['csv', 'json'])

table = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload')
def upload_form():
    return render_template('upload.html')

@app.route('/estadisticas')
def estadisticas():
    attrs_schema = request.args['attrs_schema']
    data = request.args['data']
    return render_template('estadisticas.html', attrs_schema, data)

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        files_names = ['csv', 'properties']
        cont = 0
        for name in files_names:
            if name not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files[name]
            if file.filename == '':
                flash('No file selected for uploading')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('File successfully uploaded')
                cont += 1
                if (cont == len(files_names)):
                    schema = "app/properties.schema"
                    props = "app/uploads/properties.json"
                    csvdata = "app/uploads/data.csv"

                    props = Properties(schema, props, csvdata)
                    props.printErrors()
                    table = props.getTable()
                    print(table.data)
                    return redirect('/estadisticas', attrs_schema = table.properties, data = table.data)
            else:
                flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
                return redirect(request.url)

if __name__ == "__main__":
    app.run()
