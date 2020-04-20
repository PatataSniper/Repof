import os
from io import TextIOWrapper
from app import app
from flask import flash, request, redirect, render_template, session
from werkzeug.utils import secure_filename
from app.models.properties import Properties

ALLOWED_EXTENSIONS = set(['csv', 'json'])
table = None
HOME_ROUTE = app.config['HOME_ROUTE']
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        files_names = ['csv', 'properties']
        cont = 0
        for name in files_names:
            if name not in request.files:
                flash('No file part')
                return redirect(HOME_ROUTE)
            file = request.files[name]
            if file.filename == '':
                flash('No file selected for uploading')
                return redirect(HOME_ROUTE)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                flash('File successfully uploaded')
                cont += 1
                if (cont == len(files_names)):
                    schema = "app/properties.schema"
                    props = "app/uploads/" + secure_filename(request.files['properties'].filename)
                    csvdata = "app/uploads/" + secure_filename(request.files['csv'].filename)

                    props = Properties(schema, props, csvdata)
                    if (props.checkForErrors()):
                        flash('Parsing errors:')
                        for error in props.errorMessage:
                            flash('\t'+error)
                    session['data'] = props.data
                    session['schema'] = props.props
                    print(props.props)

                    return redirect(HOME_ROUTE)
            else:
                flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
                return redirect(HOME_ROUTE)
