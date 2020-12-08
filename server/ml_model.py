import tensorflow_datasets as tfds
import numpy as np
import pandas as pd

import joblib
import zipfile

import autosklearn.classification
import autosklearn.regression

from sklearn.metrics import accuracy_score, r2_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split


def ml_text_preprocess(x_train, x_test):
    vectorizer = TfidfVectorizer()
    x_train = vectorizer.fit_transform(x_train)
    x_test = vectorizer.transform(x_test)
    return x_train, x_test


def get_model(user_slot):

    if user_slot['data_source'] == 'built_in':
        (x_train, y_train), (x_test, y_test) = tfds.as_numpy(tfds.load(user_slot['dataset'], split=[
            'train[:90%]', 'train[-10%:]'], batch_size=-1, as_supervised=True))

    else:
        if user_slot['data_type'] == 'image':
            # unzip --> train, test folders
            with zipfile.ZipFile(f"./upload/{user_slot['dataset']}", 'r') as zip_ref:
                zip_ref.extractall('./dataset/')
        elif user_slot['data_type'] == 'text':
            # .csv or .txt
            pass
        else:
            user_slot['target'] = 'charges'
            print(user_slot)
            ds = pd.read_csv("./upload/" + user_slot['dataset'])
            if user_slot['task'] == 'cls':
                labels = list(ds[user_slot['target']].unique())
                ds[user_slot['target']] = ds[user_slot['target']].apply(lambda x: labels.index(x))

            x_train, x_test, y_train, y_test = train_test_split(
                ds.drop(columns=user_slot['target']), ds[user_slot['target']], test_size=0.1)

    if user_slot['task'] == 'cls':
        if user_slot['data_type'] == 'image':
            clf = autosklearn.classification.AutoSklearnClassifier(
                memory_limit=None, time_left_for_this_task=120)
            clf.fit(x_train.reshape(x_train.shape[0], -1), y_train)
            joblib.dump(clf, 'cls_image_ml_model.pkl')
            score = accuracy_score(y_test, clf.predict(
                x_test.reshape(x_test.shape[0], -1)))

        elif user_slot['data_type'] == 'text':
            x_train_pre, x_test_pre = ml_text_preprocess(x_train, x_test)
            clf = autosklearn.classification.AutoSklearnClassifier(
                memory_limit=None, time_left_for_this_task=120)
            clf.fit(x_train_pre, y_train)
            joblib.dump(clf, 'cls_text_ml_model.pkl')
            score = accuracy_score(y_test, clf.predict(x_test_pre))

        else:
            x_train = pd.DataFrame(x_train).select_dtypes(
                include='number').to_numpy()
            x_test = pd.DataFrame(x_test).select_dtypes(
                include='number').to_numpy()
            clf = autosklearn.classification.AutoSklearnClassifier(
                memory_limit=None, time_left_for_this_task=120)
            clf.fit(x_train, y_train)
            joblib.dump(clf, 'cls_table_ml_model.pkl')
            score = accuracy_score(y_test, clf.predict(x_test))

    else:
        if user_slot['data_type'] == 'image':
            reg = autosklearn.regression.AutoSklearnRegressor(
                memory_limit=None, time_left_for_this_task=120)
            reg.fit(x_train.reshape(x_train.shape[0], -1), y_train)
            joblib.dump(reg, 'reg_image_ml_model.pkl')
            score = r2_score(y_test, reg.predict(
                x_test.reshape(x_test.shape[0], -1)))

        elif user_slot['data_type'] == 'text':
            x_train_pre, x_test_pre = ml_text_preprocess(x_train, x_test)
            reg = autosklearn.regression.AutoSklearnRegressor(
                memory_limit=None, time_left_for_this_task=120)
            reg.fit(x_train_pre, y_train)
            joblib.dump(reg, 'reg_text_ml_model.pkl')
            score = r2_score(y_test, reg.predict(x_test_pre))

        else:
            x_train = pd.DataFrame(x_train).select_dtypes(
                include='number').to_numpy()
            x_test = pd.DataFrame(x_test).select_dtypes(
                include='number').to_numpy()
            reg = autosklearn.regression.AutoSklearnRegressor(
                memory_limit=None, time_left_for_this_task=120)
            reg.fit(x_train, y_train)
            joblib.dump(reg, 'reg_text_ml_model.pkl')
            score = r2_score(y_test, reg.predict(x_test))

    mname = f"{user_slot['task']}_{user_slot['data_type']}_{user_slot['method']}_model"
    return {'model': mname, 'score': score, 'metric': 'accuracy' if user_slot['task'] == 'cls' else 'R-squared', 'summary': ''}
