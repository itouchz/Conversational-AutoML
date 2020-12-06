import nltk
import random
import string
import re

import tensorflow_datasets as tfds
import numpy as np
import pandas as pd

from nltk.stem import wordnet  # to perform lemmitization
from nltk import pos_tag  # for parts of speech
from nltk import word_tokenize  # to create tokens


GREETING_INPUTS = ["hello", "hi", "greetings", "sup",
                   "what's up", "hey", "morning", "afternoon", "evening", "night"]
CONFIRM_WORDS = ["yes", "yep", "okay", "ok", "sure", "certainly",
                 "definitely", "absolutely", "go ahead", "cool", "right", "of course"]
DENY_WORDS = ["no", "nope", "na", "not yet", "not sure",
              "more", "not", "don't", "do not", "again"]
END_WORDS = ["goodbye", "bye", "see you later",
             "end", "finish", "stop", "not anymore"]
ML_METHODS = ['machine learning', 'ml', 'machine']
DL_METHODS = ['deep learning', 'dl',
              'neural network', 'nn', 'neural', 'network']
CLASSIFICATIONS = ['class', 'classify',
                   'classification', 'classifier', 'discrete output']
REGRESSIONS = ['regress', 'regression', 'regressor', 'continuous output']
DATA_SOURCES = ['upload', '<url>', 'this data',
                'this dataset', 'my data', 'my dataset']
IMAGE_TYPES = ['image', 'picture', 'figure', 'art', 'draw', 'photo', 'photograph', 'portrait',
               'painting', 'visual', 'illustration', 'symbol', 'view', 'vision', 'sketch', 'icon']
TEXT_TYPES = ['text', 'word', 'message', 'writing', 'script', 'content', 'document', 'passage', 'context',
              'essay', 'manuscript', 'paper', 'language', 'letter', 'written', 'write', 'character', 'note', 'darft']
TABLE_TYPES = ['structured', 'structure', 'tabular', 'table', 'relation', 'database',
               'dataframe', 'frame', 'normal', 'excel', 'csv', 'file', 'summary', 'process']
# AVAIL_DATASETS = pd.read_csv('openml_datasets.csv')['name'].apply(lambda x: x.lower()).to_list()
AVAIL_DATASETS = tfds.list_builders()
TARGET_VAR = ['be dependent variable', 'be target variable', 'be dependent feature' 'be target feature',
              'variable be', 'feature be', 'value', 'feature', 'variable', 'predict', 'forecast', 'classify']  # regex ?
DELIVERY = ['by email', 'by e-mail', 'email', 'e-mail']

GREETING_RESPONSES = ["Yep, It's nice to see you here! 🙌🏻", "Hey~",
                      "*nods*", "Hi there!", "Hello", "I am glad! You are talking to me~~~"]
END_RESPONSES = ["See you then! 🙌🏻", "Bye~", "Goodluck!",
                 "Hope to see you again~", "Goodbye!~", "Thanks~"]

# simple keyword matching?
# Rule-based grammar matching


def text_normalization(text):
    text = re.sub('\-', '', text)
    text = re.sub('[^a-zA-z0-9\_]', ' ', text)  # removing special characters
    text = word_tokenize(text)  # word tokenizing
    lema = wordnet.WordNetLemmatizer()  # intializing lemmatization
    tags_list = pos_tag(text, tagset=None)  # parts of speech
    lema_words = []   # empty list
    for token, pos_token in tags_list:
        if pos_token.startswith('V'):  # Verb
            pos_val = 'v'
        elif pos_token.startswith('J'):  # Adjective
            pos_val = 'a'
        elif pos_token.startswith('R'):  # Adverb
            pos_val = 'r'
        else:
            pos_val = 'n'  # Noun
        lema_token = lema.lemmatize(token, pos_val)  # performing lemmatization
        # appending the lemmatized token into a list
        lema_words.append(lema_token)

    lema_words = [item for item in lema_words if item.lower() not in [
        'a', 'an', 'the']]
    return " ".join(lema_words)  # returns the lemmatized tokens as a sentence


user_slot = {"method": None, "task": None, "data_source": None,
             "data_type": None, "dataset": None, "target": None, "delivery": 'chat'}


def reset_slot():
    global user_slot
    user_slot = {"method": None, "task": None, "data_source": None,
                 "data_type": None, "dataset": None, "target": None, "delivery": 'chat'}


def is_slot_complete():
    return user_slot['method'] != None and user_slot['task'] != None and user_slot['data_source'] != None and user_slot['data_type'] != None and user_slot['dataset'] != None and user_slot['target'] != None and user_slot['delivery'] != None


def response_for_incomplete_slot(slot):
    return ''


def update_slot(msg):
    global user_slot

    for ml in ML_METHODS:
        if ml in msg:
            user_slot['method'] = 'ml'
            break

    for dl in DL_METHODS:
        if dl in msg:
            user_slot['method'] = 'dl'
            break

    for img in IMAGE_TYPES:
        if img in msg:
            user_slot['data_type'] = 'image'
            break

    for txt in TEXT_TYPES:
        if txt in msg:
            user_slot['data_type'] = 'text'
            break

    for table in TABLE_TYPES:
        if table in msg:
            user_slot['data_type'] = 'table'
            break

    for cl in CLASSIFICATIONS:
        if cl in msg:
            user_slot['task'] = 'cls'
            break

    for reg in REGRESSIONS:
        if reg in msg:
            user_slot['task'] = 'reg'
            break

    for ds in AVAIL_DATASETS:
        if ds in msg:
            user_slot['dataset'] = ds
            user_slot['data_source'] = 'built_in'
            user_slot['target'] = 'label'

    for ds in DATA_SOURCES:
        if ds in msg:
            user_slot['data_source'] = 'user_define'

    for d in DELIVERY:
        if d in msg:
            user_slot['delivery'] = 'email'
            break

    for tv in TARGET_VAR:
        if tv in msg:
            if tv in ['value', 'feature', 'variable', 'be target variable', 'be target feature']:
                user_slot['target'] = msg.split(tv)[0].split()[-1]
            else:
                user_slot['target'] = msg.split(tv)[-1].split()[0]


def standby_state(user_message):
    text = ''
    msg = user_message.lower()
    current_state = 'standby'
    global user_slot

    for greet in GREETING_INPUTS:
        if greet in msg:
            text += random.choice(GREETING_RESPONSES) + '\n'
            break

    for end_word in END_WORDS:
        if end_word in msg:
            current_state = 'end'
            text = random.choice(END_RESPONSES)
            break

    if current_state != 'end':
        update_slot(msg)
        if is_slot_complete():
            text += f"All you requested are well received! \n These are your requirements: {user_slot['method']}, {user_slot['task']}, {user_slot['dataset']}, {user_slot['target']}, and {user_slot['delivery']} \n Do you want to proceed?"
            current_state = 'await'
        else:
            if user_slot['data_source'] == 'user_define' and user_slot['data_source'] == None:
                text += 'Please upload your data file (.csv, .txt, .zip) below.'
            # else:
            #     text += 'Please answer a few more questions to proceed!~\n'
            #     for key, value in user_slot.items():
            #         if value == None:
            #             text += '- ' + re.sub('_', ' ', key) + '\n'

            current_state = 'active'
    else:
        current_state = 'standby'

    return text, current_state, user_slot


def active_state(user_message, await_feature=None):
    text = ''
    msg = user_message.lower()
    current_state = 'active'
    global user_slot

    for greet in GREETING_INPUTS:
        if greet in msg:
            text += random.choice(GREETING_RESPONSES) + '\n'
            break

    for end_word in END_WORDS:
        if end_word in msg:
            current_state = 'standby'
            text = random.choice(END_RESPONSES)
            break

    if current_state != 'standby':
        if await_feature != None:
            pass
        else:
            update_slot(msg)

        if is_slot_complete():
            text += f"All you requested are well received! \n These are your requirements: {user_slot['method']}, {user_slot['task']}, {user_slot['dataset']}, {user_slot['target']}, and {user_slot['delivery']} \n Do you want to proceed?"
            current_state = 'await'
        else:
            if user_slot['data_source'] == 'user_define' and user_slot['data_source'] == None:
                text += 'Please upload your data file (.csv, .txt, .zip) below.'
            # else:
            #     text += 'Thank you for your information, but please answer a few more questions.\n'
            #     for key, value in user_slot.items():
            #         if value == None:
            #             text += '- ' + re.sub('_', ' ', key) + '\n'

            current_state = 'active'

    return text, current_state, user_slot


def await_state(user_message):
    text = ''
    msg = user_message.lower()
    current_state = 'await'
    global user_slot

    for greet in GREETING_INPUTS:
        if greet in msg:
            text += random.choice(GREETING_RESPONSES) + '\n'
            break

    for end_word in END_WORDS:
        if end_word in msg:
            current_state = 'standby'
            text = random.choice(END_RESPONSES)
            break

    for con in CONFIRM_WORDS:
        if con in msg:
            current_state = 'building'
            break

    for den in DENY_WORDS:
        if den in msg:
            current_state = 'await'
            text += 'Umm... Please check your requirement~ \n'
            break

    if current_state != 'building' and current_state != 'standby':
        if is_slot_complete():
            text += f"These are your requirements: {user_slot['method']}, {user_slot['task']}, {user_slot['dataset']}, {user_slot['target']}, and {user_slot['delivery']} \n Do you want to proceed?"
            current_state = 'await'

    return text, current_state, user_slot


def building_state(user_message):
    text = ''
    current_state = 'building'
    global user_slot

    return text, current_state, user_slot


def get_response(current_state, user_message, await_feature):
    filtered_text = text_normalization(user_message)
    await_feature = await_feature

    response = {
        'standby': standby_state(filtered_text),
        'active': active_state(filtered_text, await_feature),
        'await': await_state(filtered_text),
        'building': building_state(filtered_text),
    }

    return response[current_state]
