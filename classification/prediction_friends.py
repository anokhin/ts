import sklearn



__author__ = 'Vladimir Kulpinov'

import pickle
import numpy
import csv
import user
from sklearn import svm
from sklearn import cross_validation
import random
import argparse


class FriendsPredictor(object):
    """
    Model used to predict age of users in VK
    """
    # Initializer of training model
    def __init__(self):
        numpy.random.RandomState(1)
        self.regressor = svm.SVR(C = 1000, kernel="rbf", max_iter=1000, gamma=0.6)

    # Predict friends of list user
    # return list of ages
    def predict(self, x=[]):
        return self.regressor.predict(x)

    # Train of FriendPredictor with list of users
    # and param_string
    def fit(self, x=[], y=[]):
        self.regressor.fit(x, y)
        pass

    # Save AgePredictor model in file with name filename
    def save(self, filename=None):
        if filename is None:
            filename = "predict_model.dat"
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filename):
        data = None
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
        except IOError:
            print "File {} not found".format(filename)
            exit(0)
        return data

def error_estimation(ages1, ages2):
    """
     Estimation of error of predict. Using MSE
    """
    if len(ages1) == 0 or len(ages2) != len(ages1):
        return -1
    else:
        return (sum(map(lambda x, y: abs(x - y) ** 2, ages1, ages2)) / float(len(ages1))) ** 0.5

def kfold_estimator(database_file = 'vk_base.csv'):
    """
    Function used to find best parameters for model
    with CV 80%/20%
    Input:
        database_file : csv file with users information
    """
    users = []
    with open(database_file, 'rb') as csvfile:
        vk_base_reader = csv.reader(csvfile)
        was_header = False
        for row in vk_base_reader:
            if (not was_header):
                was_header = True
            else:
                u = user.User()
                u.from_tsv(row)
                users.append(u)
                print u.to_tsv()


    print "Database is read-out"

    model = FriendsPredictor()

    numpy.random.RandomState(1)
    random.seed(1)
    random.shuffle(users)
    kf = cross_validation.KFold(len(users), n_folds=5, indices=True)
    errors = []
    for train, test in kf:
        train_x = [users[i] for i in train]
        predict_x = [users[i] for i in test]
        labels = [int(users[i].count_friends) for i in test]
        model.fit(train_x)
        cur_err =  error_estimation(labels, model.predict(predict_x).tolist())
        print cur_err
        errors.append(cur_err)

    estimation = sum(errors) / len(errors)
    print "mean value: {}".format(estimation)
    return estimation

def parse_args():
    parser = argparse.ArgumentParser(description='Linear regression method of gradient descent\nFinding number of friends')
    parser.add_argument('learn_path', nargs=1)
    parser.add_argument('test_path', nargs=1)
    return parser.parse_args()

def main():
    args = parse_args()
    users = []
    with open(args.learn_path[0], 'rb') as csvfile:
        vk_base_reader = csv.reader(csvfile)
        was_header = False
        for row in vk_base_reader:
            if (not was_header):
                was_header = True
            else:
                u = user.User()
                u.from_tsv(row)
                users.append(u)
                #print u.to_tsv()

    model = FriendsPredictor()
    x = [u.get_predictable() for u in users]
    y = [u.count_friends for u in users]
    model.fit(x, y)
    users = []

    with open(args.test_path[0], 'rb') as csvfile:
        vk_base_reader = csv.reader(csvfile)
        was_header = False
        for row in vk_base_reader:
            if (not was_header):
                was_header = True
            else:
                u = user.User()
                u.from_tsv(row)
                users.append(u)
                #print u.to_tsv()

    x = [u.get_predictable() for u in users]
    answer = model.predict(x)
    for i in answer:
        print i

if __name__ == "__main__":
    main()
