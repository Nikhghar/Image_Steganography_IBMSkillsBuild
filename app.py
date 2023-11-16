from Backend import encode,decrypt
import numpy
from numpy import asarray
from PIL import Image,ImageOps
import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template,send_file
from werkzeug.utils import secure_filename
from Crypto.Cipher import AES
import base64
import binascii

import optparse





UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','txt'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return 'No file part'
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return render_template('index.html', error='No image uploaded!')
        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],'download.jpg'))
            if request.form['go']=='encrypt':
                return redirect(url_for('image'))
            return redirect(url_for('decode1'))
        else:
            return render_template('index.html', error='Please upload an image file')
    
    return render_template('index.html')

@app.route('/image', methods=['GET', 'POST'])
def image():
    if request.method == 'POST':
        image1 = Image.open(UPLOAD_FOLDER+'download.jpg')
        # msg=request.form['msg']
        file = request.files['file']
        password = request.form['pas']
        # Convert the password string to bytes
        password_bytes = password.encode('utf-8')
        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],'message.txt'))
        # Read the content of the text file
        with open(os.path.join(app.config['UPLOAD_FOLDER'], 'message.txt'), 'r') as file:
            msg = file.read()
            print(msg)
        # Convert the msg string to bytes
        msg_bytes = msg.encode('utf-8')
        cipher = AES.new(password_bytes.rjust(16),AES.MODE_ECB)
        encoded = base64.b64encode(cipher.encrypt( msg_bytes.rjust(32) ))
        encoded_string = encoded.decode('utf-8')
        print(encoded_string)
        x=encode(image1, encoded_string)
        x.convert('RGB').save(UPLOAD_FOLDER+'new1.png')
        return send_file(UPLOAD_FOLDER+'new1.png', as_attachment=True)
    return render_template('encodepage.html')


@app.route('/decode', methods=['GET', 'POST'])
def decode1():
    if request.method == 'POST':
        password = request.form.get('pas')
        if password is None:
            return render_template('decode.html', error='Password not provided', msg=None)
        password_bytes = password.encode('utf-8')
        image1 = Image.open(UPLOAD_FOLDER + 'download.jpg')
        cipher = AES.new(password_bytes.rjust(16), AES.MODE_ECB)
        try:
            msg1 = cipher.decrypt(base64.b64decode(decrypt(image1)))
            msg1_str = msg1.decode('utf-8')
            return render_template('decode.html', msg=msg1_str, error=None)
        except Exception as e:
            return render_template('decode.html', error='Decryption error: ' + str(e), msg=None)
    
    return render_template('decode.html', error=None, msg=None)


if __name__ == '__main__':
   app.run(debug = True)