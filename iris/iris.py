"""
This file contains misc experiments on linear classifiers
"""

import argparse
import numpy
import pylab
import sklearn.datasets
from sklearn.linear_model import SGDClassifier


def select_objects(x, y, species, axis1, axis2):
    selected_items = [i for i, t in enumerate(y) if t in species]
    return x[selected_items][:, [axis1, axis2]], y[selected_items]


def plot_data_set(x, y, clf=None, description=''):
    print "Plotting data"
    pylab.figure(figsize=(10, 10))

    colors = numpy.array(['r', 'g', 'b'])[y]
    pylab.title(description, fontsize='small')
    pylab.scatter(x[:, 0], x[:, 1], marker='^', c=colors, s=100)

    if clf:
        add_decision_function_to_plot(x[:, 0].min(), x[:, 0].max(), x[:, 1].min(), x[:, 1].max(), clf)

    pylab.show()


def add_decision_function_to_plot(x_1_min, x_1_max, x_2_min, x_2_max, clf):
    x1s = numpy.linspace(x_1_min, x_1_max, 10)
    x2s = numpy.linspace(x_2_min, x_2_max, 10)

    x1, x2 = numpy.meshgrid(x1s, x2s)
    z = numpy.ones(x1.shape)

    for (i, j), v1 in numpy.ndenumerate(x1):
        v2 = x2[i, j]
        p = clf.decision_function([v1, v2])
        z[i, j] = p[0]

    pylab.contour(x1, x2, z, [0.0], colors='k', linestyles='dashed', linewidths=2.5)


def build_classifier(x, y, loss, penalty='l2'):
    print "Preparing classifier"
    sgd = SGDClassifier(loss=loss, penalty=penalty, shuffle=True, n_iter=200)
    sgd.fit(x, y)
    return sgd


def main():
    print "Welcome to the linear classification tutorial"
    args = parse_args()
    # Load Iris data set
    data = sklearn.datasets.load_iris()
    # Axes used for classification/visualization
    axis1 = 0
    axis2 = 1
    # Select objects of the specified class and axis
    x, y = select_objects(data['data'], data['target'], args.species, axis1, axis2)

    # Id -d option is set, print data set description, plot it and exit
    if args.show_desc:
        print data['DESCR']
        plot_data_set(x, y)
        exit(0)

    if len(numpy.unique(args.species)) != 2:
        print "We're working on 2-class classification for now. Sorry."
        exit(1)

    # Prepare classifier
    sgd = build_classifier(x, y, 'log')
    # Plot data set along with the decision function
    plot_data_set(x, y, clf=sgd)


def parse_args():
    parser = argparse.ArgumentParser(description='Experiments on linear classifiers applied to Iris data set')

    parser.add_argument('-d', dest='show_desc', action='store_true', default=False, help='Show data set description')

    parser.add_argument('-0', dest='species', action='append_const', const=0)
    parser.add_argument('-1', dest='species', action='append_const', const=1)
    parser.add_argument('-2', dest='species', action='append_const', const=2)

    return parser.parse_args()


if __name__ == "__main__":
    main()
