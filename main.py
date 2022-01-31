from flask import Flask, request, render_template, send_from_directory, redirect, flash, url_for, session
from flask import Flask
import youtube_dloader as yt
# import librosa
import audioextractor as ax
import bokehgen as bokgen
from waitress import serve
from datetime import datetime
import random
import pandas as pd
import os
from keras.models import load_model

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
# app.secret_key = '%\\\xdb\xe1\x99\xec\xfb\xefU\xeb\x11Gv\xac}\x92'  # Change this!
global reverb_model


@app.route('/')
def submit():
    return render_template('home.html')


@app.route('/', methods=['POST'])
def submit_post():
    if request.form["action"] == 'analysis':
        option = request.form['audiofileradio']
        print(str(option))
        if option == 'audio':
            uploaded_file = request.files['audiofile']
            if uploaded_file.filename != '':
                filepath = "./files/temp/"+ uploaded_file.filename
                uploaded_file.save(filepath)
            else:
                filepath = 'unknown'
        elif option == 'video':
            uploaded_file = request.files['videofile']
            if uploaded_file.filename != '':
                filepathvid = "./files/temp/" + uploaded_file.filename
                uploaded_file.save(filepathvid)
                filepath = ax.extract_audio(filepathvid)
            else:
                filepath = 'unknown'
        elif option == 'url':
            url = request.form['url']
            filepath = ax.extract_audio(yt.download(url))
            new_filename = filepath.replace(" ","_")
            os.rename(filepath, new_filename)
            filepath = new_filename


        if filepath == 'unknown':
            return render_template('home.html')
        else:
            bokgen.generatehtml(filepath)
        results_bokeh = './files/temp/temp.html'

        return render_template('home_return.html', results_bokeh=results_bokeh, filepath=filepath)
    else:
        filepath = request.form["filepath"]
        timestamp = datetime.now().strftime("%y_%m_%d_%H_%M_%S")
        new_filepath = './files/audios/audio_' + timestamp + os.path.splitext(filepath)[1]
        os.rename(filepath,new_filepath)

        return 'thank you for submitting'


@app.route('/contribute')
def annotate():
    dirs = ['audios', 'videos']
    random_dir = random.choice(dirs)
    random_file = random.choice(os.listdir('./files/'+random_dir))
    print(random_dir)
    print(random_file)
    filepath = "./files/" + random_dir + '/' + random_file
    filepath2 = os.path.splitext(filepath)[0]
    print (filepath2)
    print (filepath)
    return render_template('contribute.html', filepath=filepath)


@app.route('/annotate', methods=["POST","GET"])
def annotate_post():
    isTampered = request.form["isTampered"]
    filepath = request.form["filepath"]
    if isTampered == 'y':
        comments = request.form["comments"]
        seconds = request.form['tampSeconds']
    else:
        comments = '-'
        seconds = '-'
    d = {'filepath': [filepath], 'isTampered': [isTampered], 'tampering point(sec)':[seconds], 'comments' : [comments]}
    df = pd.DataFrame(data=d)
    df.to_csv(os.path.dirname(os.path.abspath(filepath))+'/annotation.csv')
    return "annotation OK"


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/results', methods=['GET', 'POST'])
def results():
    filename = request.args.get('filename')
    return render_template(filename)


@app.route('/files/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    files = "./files/"
    return send_from_directory(directory=files, filename=filename, as_attachment=True)

# starting point
if __name__ == '__main__':
    # serve(app)
    global reverb_model
    reverb_model = load_model('model_reverb.h5')
    serve(app, host='0.0.0.0', port=8000)
    # app.run()
