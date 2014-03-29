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
from sklearn.feature_extraction import DictVectorizer
import regression

from api import Api
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

    def get_user(self, uid):
        json = self.get_node(uid, fields="id,first_name,last_name,birthday,gender")
        return self.json_to_user(json)

    @staticmethod
    def get_user_first_work_year(data):
        works = data.get("work")
        if works:
            works_years = []
            for cur_work in works:
                year_start = FbApi.parse_date(cur_work.get("start_date"))
                if not year_start is None:
                    works_years.append(year_start)
            if works_years:
                return max(works_years)
        return None

    @staticmethod
    def get_user_last_education_year(data):
        works = data.get("education")
        if works:
            today_year = datetime.date.today().year
            edu_years = []
            for cur_edu in works:
                if cur_edu.get("type") == "College" and cur_edu.get("year") and cur_edu.get("year").get("name"):
                    year = int(cur_edu.get("year").get("name"))
                    if today_year - year < 100:
                        edu_years.append(today_year - year)
            if edu_years:
                return min(edu_years)
        return None

    @staticmethod
    def json_to_user(data):
        u = user.User()
        u.set_args(uid=data['id'], first_name=data['first_name'], last_name=data['last_name'])
        u.age = FbApi.parse_date(data.get('birthday'))
        u.sex = data.get('gender')
        u.relationship = data.get('relationship_status')
        u.first_work = FbApi.get_user_first_work_year(data)
        u.last_education = FbApi.get_user_last_education_year(data)
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
                years = user.User.date_to_years(date)
                return years
        return None

class RegressionSerialize:
    def __init__(self):
        """
        set dict of serialized users and file pointer to serialized file for following writing
        """
        self.file_path = "users_data_linear_regression.json"
        self.file = None

        try:
            self.file = open(self.file_path, "r")
            self.users_data = json.load(self.file)
            self.file.close()
        except IOError:
            self.users_data = {}
        except ValueError:
            self.users_data = {}

    def update_data_from_server(self):
        token = my_secrect_token.FB_TOKEN
        api = FbApi(token)

        for uid in api.get_friend_ids("me"):
            u = api.get_user(uid)
            if u.age is None:
                continue
            learn_data = u.get_data_for_regression()
            self.users_data[uid] = learn_data

    def save(self):
        self.file = open(self.file_path, "w")
        json.dump(self.users_data, self.file)
        self.file.close()

def main():
    serial = RegressionSerialize()

    print "data acquiring"
    serial.update_data_from_server()
    serial.save()

    data = serial.users_data.values()
    predict = []
    for item in data:
        predict.append(item["age"])
        del item["age"]

    dict_vectorizer = DictVectorizer()
    X = dict_vectorizer.fit_transform(data).toarray()
    X = np.nan_to_num(X) #not ideal solution
    Y = np.array(predict)

    print "training..."
    a = regression.linearRegression(X, Y)

    Y_predicted = np.dot(X, a)
    SSE_error = np.linalg.norm(Y - Y_predicted)
    print "Prediction. Relative SSE error:", SSE_error/len(Y)

    print dict_vectorizer.get_feature_names()
    print 'a=', a
    #print Y
    #print Y_predicted

if __name__ == "__main__":
    main()
