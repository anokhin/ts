"""
Facebook Graph API implementation stub
https://developers.facebook.com/docs/graph-api/reference/
"""

import re
import datetime
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn import cross_validation

import user
from api import Api
from linear_regression import FbLinRegVectorizer, LinearRegression

__author__ = 'Nikolay Anokhin'


class FbApi(Api):
    endpoint = "https://graph.facebook.com/{method}"

    def get_node(self, node, **params):
        return self.call(node, params=params)

    def get_edge(self, node, edge, **params):
        return self.call("{node}/{edge}".format(node=node, edge=edge), params=params)

    def get_friend_ids(self, uid):
        json = self.get_edge(uid, "friends", uid=uid)
        for friend in json.get("data", []):
            yield friend["id"]

    def get_user_json(self, uid):
        return self.get_node(uid, fields="id,first_name,last_name,birthday,gender")

    def get_user(self, uid):
        json = self.get_user_json(uid)
        return self.json_to_user(json)

    @staticmethod
    def json_to_user(data):
        u = user.User(data['id'], data['first_name'], data['last_name'])
        u.sex = data.get('gender')
        u.set_age(FbApi.parse_date(data.get('birthday')))
        return u

    @staticmethod
    def parse_date(date_str):
        if date_str:
            parts = re.split("[/-]", date_str)
            if len(parts) == 3:
                if date_str.find("/") > 0:
                    date = datetime.date(int(parts[2]), int(parts[0]), int(parts[1]))
                else:
                    date = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                return date
        return None

import glob
import json
import os
#create file my_secrect_token.py and define variable FB_TOKEN with facebook token there
#or comment this import if you don't want to update training set by your friends data
from my_secrect_token import FB_TOKEN

class UserSerializer:
    def __init__(self):
        """
        read user data from .json files from self.data_dir dir and write it to dict self.users_data
        """

        #dir for single .json files
        self.data_dir = "acquired_data"
        #merged dict will be writen here
        self.file_path = "users_data_merged.json"
        self.users_data = {}

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        try:
            pattern = os.path.join(self.data_dir, "*.json")
            files_to_merge = sorted(glob.glob(pattern))
            files_to_merge = map(lambda f: os.path.abspath(f), files_to_merge)
            self.file_path = os.path.abspath(self.file_path)

            if not self.file_path in files_to_merge:
                files_to_merge = [self.file_path] + files_to_merge

            for cur_filename in files_to_merge:
                cur_file = open(cur_filename, "r")
                if cur_file is None:
                    continue
                cur_data = json.load(cur_file)
                self.users_data.update(cur_data)
                cur_file.close()

        except (IOError, ValueError):
            pass

    def update_data_from_server(self):
        try:
            api = FbApi(FB_TOKEN)

            local_dict = {}

            my_json = api.get_user_json("me")
            my_id = my_json["id"]
            local_dict[my_id] = my_json

            for uid in api.get_friend_ids("me"):
                local_dict[uid] = api.get_user_json(uid)

            local_path = os.path.join(self.data_dir, "user{}.json".format(my_id))
            fp = open(local_path, "w")
            json.dump(local_dict, fp, indent=1, sort_keys=True)
            fp.close()

            self.users_data.update(local_dict)
        except (NameError, AttributeError):
            print "Token was not found. Add your token to extend learning set!"

    def save(self):
        fp = open(self.file_path, "w")
        json.dump(self.users_data, fp, indent=1, sort_keys=True)
        fp.close()

def MAE(y, y_pred):
    return mean_absolute_error(y, y_pred)


def MSRE(y, y_pred):
    return np.linalg.norm(y - y_pred)/len(y)


def RSE(y, y_pred):
    return np.sum((y - y_pred)**2) / np.sum((y_pred - y_pred.mean())**2)


def corr_error(y, y_pred):
    return 1.0 - np.corrcoef(y, y_pred)[0, 1]


def make_age_hist(y):
    plt.hist(y, bins=100, normed=True)
    plt.title(u"Age Histogram")
    plt.xlabel(u"Age")
    plt.ylabel(u"Frequency")
    plt.draw()
    plt.show()
    plt.savefig("age_histogram.png")

def main():
    serial = UserSerializer()

    print "data acquiring..."
    serial.update_data_from_server()
    serial.save()
    print "acquired smaples: %d" % (len(serial.users_data.keys()))

    print "vectorizing..."
    vectorizer = FbLinRegVectorizer()
    X, y = vectorizer.fit_transform(serial.users_data.values(), target_feature="age")
    print "valid smaples: %d" % (len(y))
    #make_age_hist(y)

    print "training..."
    lr = LinearRegression()
    lr.fit(X, y)
    y_predicted = lr.predict(X)

    print "Predicted MAE:", MAE(y, y_predicted)
    print "Predicted MSRE:", MSRE(y, y_predicted)
    print "Predicted RSE:", RSE(y, y_predicted)
    print "Predicted Correlation:", corr_error(y, y_predicted)

    cv_num = 5

    scores = cross_validation.cross_val_score(lr, X, y, cv=cv_num, scoring=MAE, score_func=MAE)
    print scores, "Cross-validation MAE: %f" % (scores.mean())

    scores = cross_validation.cross_val_score(lr, X, y, cv=cv_num, scoring=MSRE, score_func=MSRE)
    print scores, "Cross-validation MSRE: %f" % (scores.mean())

    scores = cross_validation.cross_val_score(lr, X, y, cv=cv_num, scoring=RSE, score_func=RSE)
    print scores, "Cross-validation RSE: %f" % (scores.mean())

    scores = cross_validation.cross_val_score(lr, X, y, cv=cv_num, scoring=corr_error, score_func=corr_error)
    print scores, "Cross-validation corr_error: %f" % (scores.mean())

    print "Features:", vectorizer.get_feature_names()
    print "Features coefs:", lr.train_coefs

if __name__ == "__main__":
    main()