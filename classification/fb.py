"""
Facebook Graph API implementation stub
https://developers.facebook.com/docs/graph-api/reference/
"""

import sys
import re
import datetime
import user
import json

import numpy as np
from linear_regression import FbLinRegVectorizer, LinearRegression
from api import Api

#create file my_secrect_token.py and define variable FB_TOKEN with facebook token there
#or comment this import if you don't want to update training set by your friends data
import my_secrect_token

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
                years = int((date.today() - date).days / 365.2425)
                return years
        return None


class UserSerializer:
    def __init__(self):
        """
        read user data from file to dict self.users_data
        """
        self.file_path = "users_data_linear_regression.json"
        self.file = None
        try:
            self.file = open(self.file_path, "r")
            self.users_data = json.load(self.file)
            self.file.close()
        except (IOError, ValueError):
            self.users_data = {}

    def update_data_from_server(self):
        try:
            token = my_secrect_token.FB_TOKEN
            api = FbApi(token)

            for uid in api.get_friend_ids("me"):
                self.users_data[uid] = api.get_user_json(uid)

        except (NameError, AttributeError):
            print "Token was not found. Add your token to extend learning set!"

    def save(self):
        self.file = open(self.file_path, "w")
        json.dump(self.users_data, self.file, indent=1, sort_keys=True)
        self.file.close()

def main():
    serial = UserSerializer()

    print "data acquiring..."
    serial.update_data_from_server()
    serial.save()

    print "vectorizing..."
    vectorizer = FbLinRegVectorizer()
    X, y = vectorizer.fit_transform(serial.users_data.values(), target_feature="age")

    print "training..."
    lr = LinearRegression()
    lr.fit(X, y)
    y_predicted = lr.predict(X)

    SSE_error = np.linalg.norm(y - y_predicted)
    print "Prediction. Relative SSE error:", SSE_error/len(y)

    print vectorizer.get_feature_names()
    print 'a=', lr.train_coefs

if __name__ == "__main__":
    main()
