import tensorflow as tf
import autokeras as ak
import tensorflow_datasets as tfds
import numpy as np
import pandas as pd

import zipfile

from sklearn.metrics import accuracy_score, r2_score
from tensorflow.keras.models import load_model

def save_model(model, name):
    try:
        model.save(name, save_format="tf")
    except:
        model.save(name + ".h5")


es = tf.keras.callbacks.EarlyStopping(patience=2, restore_best_weights=True)


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
            ds = pd.read_csv("./upload/" + user_slot['dataset'])
            labels = list(ds[user_slot['target']].unique())
            ds[user_slot['target']] = ds[user_slot['target']].apply(
                lambda x: labels.index(x))
            x_train, x_test, y_train, y_test = train_test_split(
                ds.drop(columns=user_slot['target']), ds[user_slot['target']], test_size=0.1)

    if user_slot['task'] == 'cls':
        if user_slot['data_type'] == 'image':
            clf = ak.ImageClassifier(
                overwrite=True, max_trials=2, objective='val_accuracy')
            clf.fit(x_train, y_train, epochs=10,
                    validation_split=0.10, callbacks=[es])
            model = clf.export_model()
            save_model(model, 'cls_image_dl_model')
            score = accuracy_score(y_test, np.argmax(
                model.predict(x_test), axis=1))

        elif user_slot['data_type'] == 'text':
            clf = ak.TextClassifier(
                overwrite=True, max_trials=10, objective='val_accuracy')
            clf.fit(x_train, y_train, epochs=10,
                    validation_split=0.10, callbacks=[es])
            model = clf.export_model()
            save_model(model, 'cls_text_dl_model')
            score = accuracy_score(y_test, np.argmax(
                model.predict(x_test), axis=1))

        else:
            x_train = pd.DataFrame(x_train).select_dtypes(
                include='number').to_numpy()
            x_test = pd.DataFrame(x_test).select_dtypes(
                include='number').to_numpy()
            clf = ak.StructuredDataClassifier(
                overwrite=True, max_trials=2, objective='val_accuracy')
            clf.fit(x_train, y_train, epochs=10,
                    validation_split=0.10, callbacks=[es])
            model = clf.export_model()
            save_model(model, 'cls_table_dl_model')
            score = accuracy_score(y_test, np.argmax(
                model.predict(x_test), axis=1))

    else:
        if user_slot['data_type'] == 'image':
            reg = ak.ImageRegressor(overwrite=True, max_trials=2)
            reg.fit(x_train, y_train, epochs=10,
                    validation_split=0.10, callbacks=[es])
            model = reg.export_model()
            save_model(model, 'reg_image_dl_model')
            score = r2_score(y_test, model.predict(x_test))

        elif user_slot['data_type'] == 'text':
            reg = ak.TextRegressor(overwrite=True, max_trials=2)
            reg.fit(x_train, y_train, epochs=10,
                    validation_split=0.10, callbacks=[es])
            model = reg.export_model()
            save_model(model, 'cls_text_dl_model')
            score = r2_score(y_test, model.predict(x_test))

        else:
            x_train = pd.DataFrame(x_train).select_dtypes(
                include='number').to_numpy()
            x_test = pd.DataFrame(x_test).select_dtypes(
                include='number').to_numpy()
            reg = ak.StructuredDataRegressor(overwrite=True, max_trials=2)
            reg.fit(x_train, y_train, epochs=10,
                    validation_split=0.10, callbacks=[es])
            model = reg.export_model()
            save_model(model, 'cls_table_dl_model')
            score = r2_score(y_test, model.predict(x_test))

    mname = f"{user_slot['task']}_{user_slot['data_type']}_{user_slot['method']}_model"
    return {'model': mname, 'score': score, 'metric': 'accuracy' if user_slot['task'] == 'cls' else 'R-squared', 'summary': ''}
