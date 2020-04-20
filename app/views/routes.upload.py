class Upload:
    def __init__(self):
        pass

    @app.route('/upload')
    def upload_form():
        return render_template('upload.html')

    redirect_route = '/upload'
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
                        return redirect(redirect_route)
                else:
                    flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
                    return redirect(request.url)