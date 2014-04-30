import argparse
from matplotlib.cm import get_cmap
import os
import json as JSON
import numpy
import pylab
import numpy.random
import sklearn.datasets
import sklearn.svm
from datetime import date
from sklearn.cross_validation import cross_val_score
from sklearn.metrics import make_scorer
from math import sqrt
import re

__author__ = 'Ilia Taraban'




def RMSE(ground_truth, predictions):
    err = (predictions - ground_truth) ** 2
    result = float(err.sum()) / predictions.size
    return sqrt(result)


def MAE(ground_truth, predictions):
    err = abs(predictions - ground_truth)
    result = float(err.sum()) / predictions.size
    return result

def RSE(ground_truth, predictions):
    m_ground = ground_truth.mean()
    #m_predict = predictions.mean()
    err = (predictions - ground_truth) ** 2
    m = (ground_truth - m_ground) ** 2
    if m.sum() == 0:
        print "OOOOOOOOps - rse"
        return err.sum()
    err_sum = err.sum()
    m_sum = m.sum()
    result = err_sum/ m_sum
    return result

def correlation(ground_truth, predictions):
    m_ground = ground_truth.mean()
    m_predict = predictions.mean()
    size = predictions.size
    st = float(((ground_truth - m_ground) ** 2).sum() / (size - 1))
    sy = float(((predictions - m_predict) ** 2).sum() / (size - 1))
    sty = float(((predictions - m_predict) * (ground_truth - m_ground)).sum() / (size - 1))
    if st * sy == 0:

        return 1
    return 1 - abs(sty / (st * sy))




def get_features(user):
    x = numpy.empty((1, 11))

    #college count
    edu_count = 0.0
    if user.has_key('education'):
        educ_list = user['education']
        edu_count = len(educ_list)
    #iOS device flag
    x[0][0] = float(edu_count)
    ios = 0
    android = 0
    if user.has_key('devices'):
        dev = user['devices']
        if isinstance(dev, list):
            for i in dev:
                if i.has_key('os'):
                    if i['os'] == 'Android':
                        android = 1
                    if i['os'] == 'iOS':
                        ios = 1
        else:
            if dev.has_key('os'):
                if dev['os'] == 'Android':
                    android = 1
                if dev['os'] == 'iOS':
                    ios = 1
    x[0][1] = float(android)
    x[0][2] = float(ios)
    gender = -1
    if user.has_key('gender'):
        gender = 1
        if user['gender'] == 'male':
            gender = 2
    x[0][3] = float(gender)
    #work count
    work_count = 0
    if user.has_key('work'):
        work_list = user['work']
        work_count = len(work_list)
    x[0][4] = float(work_count)
    #relation type
    relation_type = 0
    if user.has_key('relationship_status'):
        status = user['relationship_status']
        if status == 'Single':
            relation_type = 1

    x[0][5] = float(relation_type)
    #books count
    books_count = 0
    if user.has_key('books'):
        books_count = len(user['books'])
    #music count
    music_count = 0
    if user.has_key('music'):
        music_count = len(user['music'])
    #movies count
    movies_count = 0
    if user.has_key('movies'):
        movies_count = len(user['movies'])
    #posts count

    x[0][6] = float(books_count)
    x[0][7] = float(music_count)
    x[0][8] = float(movies_count)

    posts_count = 0
    #post per time
    post_aver = 0
    if user.has_key('posts'):
        posts = user['posts']['data']
        posts_count = len(posts)
        last = posts[0]['created_time']
        last_list = last[:10].split('-')
        last_date = date(int(last_list[0]) , int(last_list[1]), int(last_list[2]))
        current = posts[posts_count - 1]['created_time']
        curr_list = current[:10].split('-')
        curr_date = date(int(curr_list[0]) , int(curr_list[1]), int(curr_list[2]))
        sub = float((last_date - curr_date).days)

        post_aver = abs(sub / posts_count)


    x[0][9] = float(posts_count)
    x[0][10] = float(post_aver)
    return x


def get_friends_features():
    ylist = []
    x = numpy.empty((0, 11))
    #for filename in os.listdir('friends'):
    #    file = open('./friends/' + filename, 'r')
    #    json = JSON.load(file)
    file = open('users_data_merged.json', 'r')
    united_json = JSON.load(file)
    for e in united_json:
        json = united_json[e]

        if json.has_key('birthday') and len(json['birthday']) > 8:
            x1 = get_features(json)

            birthday = json['birthday']
            y1 = int(birthday.split('/')[2])
            ylist.append(y1)
            x = numpy.vstack((x, x1))
    y = numpy.array(ylist)
    y = 2014 - y
    y = (y > 19) * (y - 19)  + 19
    y = (y < 40) * (y - 40)  + 40
    return x, y


def select_model(x, y):

    model = sklearn.svm.SVC()
    print "Trying model {}".format(model)
    model.fit(x, y)


    model = []
    for i in [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]:

        rmse_scorer = make_scorer(RMSE, greater_is_better=False)
        mae_scorer = make_scorer(MAE, greater_is_better=False)
        rse_scorer = make_scorer(RSE, greater_is_better=False)
        corr_scorer = make_scorer(correlation, greater_is_better=False)

        modelrbf = sklearn.svm.SVC(C=i, kernel='rbf')
        model.append((modelrbf, "rbf", i))
        modellinear = sklearn.svm.SVC(C=i, kernel='linear')
        model.append((modellinear, "linear", i))

        modelpoly2 = sklearn.svm.SVC(C=i, kernel='poly', degree=2)
        model.append((modelpoly2, "poly2", i))
        modelpoly3 = sklearn.svm.SVC(C=i, kernel='poly', degree=3)
        model.append((modelpoly3, "poly3", i))
        modelsigmoid = sklearn.svm.SVC(C=i, kernel='sigmoid')
        model.append((modelsigmoid, "sigmoid", i))
    for j in [(mae_scorer, "mae"), (rmse_scorer, "rmse"), (rse_scorer, "rse"), (corr_scorer, "corr")]:
        scoring(model, j[0], x, y, j[1])


    return model


def scoring(model ,func, x, y, name):
    minscores = abs((cross_val_score(model[0][0], x, y, scoring=func)).mean())
    best = model[0]
    for j in model:
        scores = cross_val_score(j[0], x, y, scoring=func)
        #print "Trying model {}".format(j[0])
        if minscores > abs(scores.mean()):
            minscores = abs(scores.mean())
            best = j
    bestmodel = best[0]
    if name == "corr":
        print best[1], best[2], "by scoring ", 1 - minscores, "using ", name
    else:
        print best[1], best[2], "by scoring ", minscores, "using ", name


def main():
    print "## Welcome to the Text Mining tutorial ##"
    x, y = get_friends_features()
    clf = select_model(x, y)




if __name__ == "__main__":
    main()
