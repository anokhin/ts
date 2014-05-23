import argparse
import math
import numpy

import pylab
import sklearn.cross_validation as cv

from sklearn.datasets import load_digits
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier


__author__ = 'nikolayanokhin'


def load_data_set(n=10):
    print "Loading digits of %d classes" % n
    return load_digits(n)


def evaluate_model(model, x_train, y_train, x_test, y_test):
    model.fit(x_train, y_train)
    y_train_pred = model.predict(x_train)
    y_test_pred = model.predict(x_test)
    return accuracy_score(y_train_pred, y_train), accuracy_score(y_test_pred, y_test)


def show_images(model, x):
    rows = cols = math.ceil(math.sqrt(x.shape[0]))

    for i in xrange(x.shape[0]):
        datum = x[i]
        y = model.predict(datum)

        ax = pylab.subplot(rows, cols, i + 1)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        ax.text(-0.5, -0.8, "class=%d" % y[0])
        pylab.gray()
        pylab.matshow(datum.reshape(8, 8), 0)

    pylab.show()


def main():
    print "Welcome to the Ensemble tutorial"
    args = parse_args()

    digits = load_data_set()

    if args.show_desc:
        print digits['DESCR']
        exit(0)

    x_train, x_test, y_train, y_test = cv.train_test_split(digits.data, digits.target)

    n = 300
    acc_train = numpy.zeros(n)
    acc_test = numpy.zeros(n)
    t = numpy.arange(n) + 1

    for i in xrange(n):
        k = t[i]
        model = RandomForestClassifier(n_estimators=k)
        atr, ats = evaluate_model(model, x_train, y_train, x_test, y_test)
        acc_train[i] = 1 - atr
        acc_test[i] = 1 - ats

    pylab.plot(t, acc_train, 'r')
    pylab.plot(t, acc_test, 'b')
    pylab.show()

    model = DecisionTreeClassifier()

    if args.show:
        show_images(model, x_test[:args.show])


def parse_args():
    parser = argparse.ArgumentParser(description='Digit recognition using ensemble models')
    parser.add_argument('-d', dest='show_desc', action='store_true', default=False, help='Show data set description')
    parser.add_argument('-s', dest='show', type=int, default=0, help='Number of images from test set to show')
    return parser.parse_args()


if __name__ == "__main__":
    main()
