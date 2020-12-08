from flask import Flask, request, send_from_directory
from flask_cors import CORS
from tensorflow.keras.models import load_model

import tensorflow as tf
import autokeras as ak
import numpy as np

import dl_model as dl
import ml_model as ml

import os
import joblib

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def index():
    return 'Conversational AutoML Server~!'

@app.route('/img/<path:filename>', methods=['GET', 'POST'])
def img_download(filename):
    uploads = os.path.join(app.root_path, 'upload/')
    return send_from_directory(directory=uploads, filename=filename)

@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(app.root_path, 'models/')
    return send_from_directory(directory=uploads, filename=filename)


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file.save('./upload/' + file.filename)
    results = rb.upload_success(request.form['current_state'], file.filename)
    return {'sender': 'Bot', 'text': 'Successfully uploaded! <br/ >' + results[0], 'current_state': results[1], 'user_slot': results[2]}


@app.route('/image/get_prediction', methods=['POST'])
def get_image_prediction():
    file = request.files['file']
    file.save('./upload/' + file.filename)

    model_name = request.form['model']
    label_name = request.form['target'].split(',')
    [task, _, method, _] = model_name.split('_')
    text = ''

    img = tf.keras.preprocessing.image.load_img("./upload/" + file.filename, target_size=(32, 32))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)

    print(label_name)
    if method == 'dl':
        if task == 'cls':
            if len(label_name) == 2:
                model = load_model(
                    model_name, custom_objects=ak.CUSTOM_OBJECTS)
                pred = np.floor(model.predict([img_array]))
                text += "It's a " + label_name[pred[0]] + "."
            else:
                model = load_model(
                    model_name, custom_objects=ak.CUSTOM_OBJECTS)
                pred = np.argmax(model.predict([img_array]), axis=1)
                text += "It's a " + label_name[pred[0]] + "."
        else:
            model = load_model(model_name, custom_objects=ak.CUSTOM_OBJECTS)
            pred = model.predict([img_array])
            text += "The predicted " + label_name + " is " + pred + "."
    else:
        img_array = img_array.numpy().reshape(1,-1)
        if task == 'cls':
            model = joblib.load(model_name)
            pred = model.predict([img_array])
            text += "It's a " + label_name[pred[0]] + "."
        else:
            model = joblib.load(model_name)
            pred = model.predict([img_array])
            text += "The predicted " + label_name + " is " + pred + "."

    response = {
        'sender': 'Bot',
        'text': text, 
        'img_name': file.filename
    }

    return response


@app.route('/text/get_prediction', methods=['POST'])
def get_text_prediction():
    model_name = request.get_json(force=True)['model']
    label_name = request.get_json(force=True)['target']
    input_text = request.get_json(force=True)['input_text']
    [task, _, method, _] = model_name.split('_')
    text = ''

    print(label_name)
    if method == 'dl':
        if task == 'cls':
            if len(label_name) == 2:
                model = load_model(
                    model_name, custom_objects=ak.CUSTOM_OBJECTS)
                pred = np.round(model.predict([input_text])).astype(int)
                print(pred)
                text += "It's " + label_name[pred[0][0]] + "."
            else:
                model = load_model(
                    model_name, custom_objects=ak.CUSTOM_OBJECTS)
                pred = np.argmax(model.predict([input_text]), axis=1).astype(int)
                text += "It's " + label_name[pred[0][0]] + "."
        else:
            model = load_model(model_name, custom_objects=ak.CUSTOM_OBJECTS)
            pred = model.predict([input_text])
            text += "The predicted " + label_name + " is " + pred + "."
    else:
        if task == 'cls':
            model = joblib.load(model_name)
            pred = model.predict([input_text])
            text += "It's " + label_name[pred[0]] + "."
        else:
            model = joblib.load(model_name)
            pred = model.predict([input_text])
            text += "The predicted " + label_name + " is " + pred + "."

    response = {
        'sender': 'Bot',
        'text': text
    }

    return response


@app.route('/get_model', methods=['POST'])
def get_model():
    data = request.get_json(force=True)

    if data['user_slot']['method'] == 'dl':
        results = dl.get_model(data['user_slot'])
    else:
        results = ml.get_model(data['user_slot'])

    response = {
        'model': results['model'],
        'score': results['score'],
        'metric': results['metric'],
        'summary': results['summary']
    }

    return response
