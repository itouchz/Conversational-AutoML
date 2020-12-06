from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def index():
    return 'Pinging Model Application!!'


@app.route('/greet', methods=['GET'])
def first_greet():
    return {'sender': 'Bot', 'text': "Hi 👋🏻! I'm your model builder🧑🏻‍💻~ Just tell me which model do you want by simply following the examples below👇🏻."}


@app.route('/bot', methods=['POST'])
def bot():
    response = {
        'sender': 'Bot',
        'text': 'Bot Response!'
    }

    return response
