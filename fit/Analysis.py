import time
import numpy as np
import csv
import matplotlib.pyplot as plt
import pickle
import pandas as pd
from matplotlib.legend_handler import HandlerLine2D
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor

# --------stable-------------------
import os, sys

path = os.getcwd()
parent_path = os.path.dirname(path)
sys.path.append(parent_path)

import static_data as sd

CURRENT_PATH = sd.CURRENT_PATH
ARTIST_FOLDER = sd.ARTIST_FOLDER
USER_FOLDER = sd.USER_FOLDER
ARTIST = sd.ARTIST
SONGS = sd.SONGS
SONG_P_D_C = sd.SONG_P_D_C
ARTIST_P_D_C = sd.ARTIST_P_D_C
USER_P_D_C = sd.USER_P_D_C
SONG_FAN = sd.SONG_FAN
ARTIST_FAN = sd.ARTIST_FAN
DAYS = sd.DAYS
START_UNIX = sd.START_UNIX
DAY_SECOND = sd.DAY_SECOND
START_WEEK = sd.START_WEEK
ALL_USER = sd.ALL_USER
ALL_USER_INFO = sd.ALL_USER_INFO
USER_SONG_RELATION = sd.USER_SONG_RELATION
USER_SONG_FOLDER = sd.USER_SONG_FOLDER
ALL_SONG = sd.ALL_SONG
SONG_INFO = sd.SONG_INFO
USER_INFO_FILTER = sd.USER_INFO_FILTER
SONG_FEATURE = sd.SONG_FEATURES
SONG_UNIQUE_USER = sd.SONG_UNIQUE_USER
TRAINING_LABEL = sd.TRAINING_LABEL
RECENT_DAYS_LIST = [1, 2, 3, 7, 14, 21, 28, 35, 42, 49, 56]


def generateFeatures(doAnyway=False):
    if not doAnyway:
        if os.path.exists(SONG_FEATURE) and os.path.exists(TRAINING_LABEL):
            ret = pickle.load(open(SONG_FEATURE, 'rb'))
            trl = pickle.load(open(TRAINING_LABEL, 'rb'))
            return ret, trl
    song_features = {}
    songInfo = pickle.load(open(SONG_INFO, 'rb'))
    songFans = pickle.load(open(SONG_UNIQUE_USER, 'rb'))
    training_label = {}
    for i in songInfo:
        features = []
        label = []
        print("%s len of day: %d" % (i, len(songInfo[i][0])))
        for dt in range(60, 120, 1):
            feature = []
            for day in RECENT_DAYS_LIST:
                feature.append(np.sum(songInfo[i][0][dt - day:dt]))
                feature.append(np.sum(songInfo[i][1][dt - day:dt]))
                feature.append(np.sum(songInfo[i][2][dt - day:dt]))
                feature.append(
                    0 if songFans.get(i) is None else np.sum([len(songFans[i][j]) for j in range(dt - day, dt)]))
                # print(songFans)
            label.append(songInfo[i][0][dt])
            features.append(feature)
        label = np.asarray(label).reshape(len(label), 1)
        training_label[i] = label
        song_features[i] = features
    # pickle.dump(song_features,open(SONG_FEATURE,'wb'))

    pickle.dump(training_label, open(TRAINING_LABEL, 'wb'))
    return song_features, training_label

def generateTestData(label_data,dt):
    songInfo = pickle.load(open(SONG_INFO, 'rb'))
    songFans = pickle.load(open(SONG_UNIQUE_USER, 'rb'))
    feature = []
    for day in RECENT_DAYS_LIST:
        feature.append(np.sum(label_data[dt - day:dt]))
        feature.append(0)
        feature.append(0)
        feature.append(
            0 if songFans.get(i) is None else np.sum([len(songFans[i][j]) for j in range(dt - day, dt)]))
        # print(songFans)
    return feature


def trainModelUsingRFR(training_data, label_data):  # RFR:RandomForestRegressor
    model = RandomForestRegressor()
    model.fit(training_data,label_data)
    for i in range(120,184,1):
        feature = generateTestData(label_data,i)
        ret = model.predict(feature)
        print(ret)
        label_data.append(ret)

if __name__ == "__main__":
    songFeature, training_label = generateFeatures()
    for i in songFeature:
        training_data = pd.DataFrame(np.asmatrix(songFeature[i]))
        if os.path.exists(i + ".csv"):
            training_data.to_csv(i + ".csv")
        trainModelUsingRFR(songFeature[i],training_label[i])