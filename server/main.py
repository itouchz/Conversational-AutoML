from flask import Flask, request
from flask_cors import CORS
import CA

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def index():
    return 'Conversational AutoML Server~!'


@app.route('/greet', methods=['GET'])
def first_greet():
    return {'sender': 'Bot', 'text': "Hi 👋🏻! I'm your model builder🧑🏻‍💻~ Just tell me which model do you want by simply following the examples below👇🏻."}


@app.route('/reset', methods=['GET'])
def reset():
    CA.rule_based_reset()
    return {'sender': 'Bot', 'text': "Hi 👋🏻! I'm your model builder🧑🏻‍💻~ Just tell me which model do you want by simply following the examples below👇🏻."}


@app.route('/bot', methods=['POST'])
def bot():
    data = request.get_json(force=True)
    results = CA.rule_based_response(
        data['currentState'], data['message'], None)

    response = {
        'sender': 'Bot',
        'text': results[0],
        'current_state': results[1],
        'user_slot': results[2]
    }

    return response
