import os
import json
import ast
from zipfile import ZipFile
from app import app
from flask import send_from_directory, redirect, request

HOME_ROUTE = app.config['HOME_ROUTE']
ROOT_FOLDER = app.config['ROOT_FOLDER']
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
DATA_FOLDER = app.config['DATA_FOLDER']

def updateProperties(props):
    with open(ROOT_FOLDER + DATA_FOLDER + 'properties.json', 'w') as f:
        json.dump(ast.literal_eval(props), f)
        f.close()

def updateCSV(csv):
    with open(ROOT_FOLDER + DATA_FOLDER + 'data.csv', 'w') as f:
        for instance in csv:
            for value in instance:
                f.write(value)
        f.close()

def get_all_file_paths(directory):
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            if (filename.rsplit('.', 1)[-1].lower() == 'zip'):
                continue
            filepath = '.' + DATA_FOLDER + filename
            file_paths.append(filepath)

    return file_paths

def zip():
    directory = ROOT_FOLDER + DATA_FOLDER
    file_paths = get_all_file_paths(directory)

    with ZipFile(ROOT_FOLDER + DATA_FOLDER + 'data.zip','w') as zip:
        for file in file_paths:
            zip.write(file)

@app.route('/data', methods=['POST'])
def download():
    csv = []
    if request.method == "POST":
        i = -1
        while(request.form.get("csv["+str(i:=i+1)+"]")):
            json = request.form["csv["+str(i)+"]"]
            csv.append(request.form["csv["+str(i)+"]"])

        updateProperties(request.form['properties'])
        updateCSV(csv)
        zip()

        return send_from_directory(ROOT_FOLDER + DATA_FOLDER, 'data.zip', as_attachment=True)
