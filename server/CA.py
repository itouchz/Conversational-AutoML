from flask import Flask, request
from flask_cors import CORS

import rule_based as rb

import os

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def index():
    return 'Conversational AutoML Server~!'


@app.route('/greet', methods=['GET'])
def first_greet():
    return {'sender': 'Bot', 'text': "Hi 👋🏻! I'm your model builder🤖~ <br/> Just tell me what kind of model do you want."}


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file.save('./upload/' + file.filename)
    results = rb.upload_success(request.form['current_state'], file.filename)
    return {'sender': 'Bot', 'text': 'Successfully uploaded! <br/ >' + results[0], 'current_state': results[1], 'user_slot': results[2]}


@app.route('/reset', methods=['GET'])
def reset():
    rb.reset_slot()
    return {'sender': 'Bot', 'text': "Hi 👋🏻! I'm your model builder🤖~ <br/> Just tell me what kind of model do you want."}


@app.route('/bot', methods=['POST'])
def bot():
    data = request.get_json(force=True)
    results = rb.get_response(data['currentState'], data['message'], None)

    response = {
        'sender': 'Bot',
        'text': results[0],
        'current_state': results[1],
        'user_slot': results[2]
    }

    return response
