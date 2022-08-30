from flask import Flask,render_template,request,redirect,url_for
from speech_recognition import *
from pydub import AudioSegment
import os 

app = Flask(__name__)
@app.route("/")
def index():
    return render_template('index.html')

@app.route('/menu_page')
def menu_page():
    return render_template("menu.html")



@app.route('/service-worker.js')
def sw():
    return app.send_static_file('service-worker.js')

@app.route("/contact_page")
def contact():
    return render_template("contact.html")


@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        return redirect(url_for('menu_page'))

def convert_audio(input_path):
    src = input_path
    dst = "audio/test.wav"

    # convert wav to mp3                                                            
    sound = AudioSegment.from_file(src)
    sound.export(dst, format="wav")
    return dst


if __name__ == '__main__':
   app.run(debug = True)
