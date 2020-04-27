import os
import app.models.learning as learning
import app.models.parse as parse
from app import app
from flask import render_template

@app.route('/')
def index():
    DATA_FOLDER = app.config['DATA_FOLDER']
    
    data_filename = 'data.csv'
    data_filepath = os.path.join(DATA_FOLDER, data_filename)
    props_filename = 'props.json'
    props_filepath = os.path.join(DATA_FOLDER, props_filename)

    data = parse.read_csv(data_filepath)
    props = parse.read_json(props_filepath)
    props['data'] = data

    attrs = [ key for json in props['attributes'] for key in json ]

    data = []
    for instance in props['data']:
        for i in range(len(attrs)):
            if attrs[i] == props['target']:
                data.append(instance[i])

    classes = []
    for x in data:
        if x not in classes:
            classes.append(x)

    freqs = learning.zero_r(classes, data)
    acc = learning.zero_r_accuracy(freqs)
    n = len(freqs)

    return render_template('zero_r.html', props = props, classes = classes, freqs = freqs, acc = acc, n = n)

if __name__ == '__main__':
    app.run()