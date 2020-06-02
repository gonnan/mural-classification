import json
import urllib.request
import os
from werkzeug.utils import secure_filename
from fastai.vision import *

from flask import Flask, flash, request, redirect, render_template
from flask import request
from flask import send_from_directory


UPLOAD_PATH = Path('./uploads')
ALLOWED_EXTENSIONS = {'jpeg', 'jpg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_PATH


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
@app.route('/home')
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            file.save(file_path)
            pred = get_predictions(file_path)

            # Finds the appropriate entry for the predicted mural
            for artist in artists:
                if pred == (artist['artist'] + ' ' + artist['year']):
                    return render_template('artist.html', artist=artist, image=file_path)

    return render_template('home.html', artists=artists)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


def get_predictions(image):
    path = Path('.')
    defaults.device = torch.device('cpu')

    learner = load_learner(path, 'model.pkl')

    img = open_image(image)
    pred_class,pred_idx,outputs = learner.predict(img)

    return str(pred_class)



with open('artist_info.txt') as json_file:
    artists = json.load(json_file)

artists = artists['artists']

if __name__ == '__main__':
    app.run(debug=True)