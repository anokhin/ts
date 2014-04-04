""" This module contains some utility procedures for classifier
Main algorithm: you need to create Classifier with desired parameters (build_classifier.__doc__),
choose targets of CSV-file (choose_targets.__doc__),
pre-process CSV-file with features and targets (read_data_set.__doc__),
Classifier.fit: build classification tree with pre-processed data,
Classifier.predict
"""
import StringIO
import argparse
import numpy
import scipy.stats
import sklearn.feature_extraction
import pydot
from myTree import MyClassifier
from myTree import BinaryTree

TARGET = "target"


def choose_targets(source=2):
    """
    0 = VK - CSV - file
    1 = DT Tutorial (Seminar task)
    2 = VK
    :return: chosen columns for classification
    """
    if source == 0:
        columns = {
            "status_len": (5, parse_int),
            "m_friends": (10, parse_int),
            "sex": (2, parse_int),
            "rel": (4, parse_int),
            "emo": (6, parse_int),
            TARGET: (3, parse_int)
        }
        return columns
    elif source == 1:
        columns = {
            "age": (4, parse_int),
            "gender": (5, parse_int),
            "education": (29, parse_string),
            TARGET: (54, parse_int)
        }
        return columns
    elif source == 2:
        columns = {
            "friends": (15, parse_int),
            "grad_year": (18, parse_int),
            "emotions": (6, parse_int),
            "albums": (14, parse_int),
            TARGET: (3, parse_int)
        }
        return columns


def read_data_set(columns, ds_path='data/data.csv', with_targets=True):
    """ Parse CSV-file, choose no-None data

    :param ds_path: CSV-file path
    :param columns: returned from choose_targets
    :return: x(n x m), y(n x 1), feature_names
    """
    data = []
    targets = []
    with open(ds_path, 'rU') as ds_file:
        for line in ds_file:
            items = line.strip().split('\t')

            row = {}
            target = None
            row_valid = True
            for name, (column, parse_fun) in columns.iteritems():
                value = parse_fun(items[int(column) - 1])
                if value is None:
                    row_valid = False
                    break
                if name == TARGET:
                    target = value
                else:
                    row[name] = value

            if with_targets:
                if row_valid and row and target:
                    data.append(row)
                    targets.append(target)
            else:
                # For clf.predict()
                if row_valid and row:
                    data.append(row)

    dv = sklearn.feature_extraction.DictVectorizer()
    return dv.fit_transform(data).todense(), numpy.array(targets), dv.get_feature_names()


def print_set_stats(ds, target, feature_names):
    print "Data set contains {} items and {} features".format(ds.shape[0], ds.shape[1])

    def print_distribution(x):
        for value, count in scipy.stats.itemfreq(x):
            print "{value}\t{count}".format(value=value, count=count)

    for i, name in enumerate(feature_names):
        print "Feature: {}".format(name)
        print_distribution(ds[:, i])

    print "Target"
    print_distribution(target)


def build_classifier(min_delta_imp=30, min_list_size=2, max_tree_node_amount=100):
    """ Build classifier
    :param min_delta_imp: (=30) split-stopping criteria
    :param min_list_size: (=2) -||-
    :return: Classifier
    """
    return MyClassifier(min_delta_imp, min_list_size, max_tree_node_amount)


def parse_int(s):
    return int(s) if s != "-1" else None


def parse_string(s):
    return s if s != "-1" else None


def main():
    args = parse_args()

    print "parsed"

    #VK
    columns = choose_targets(2)
    x, y, feature_names = read_data_set(columns=columns, ds_path='data/data.csv')
    print_set_stats(x, y, feature_names)

    cls = build_classifier(30, 2, 100)
    model = cls.fit(x, y)
    model.draw_me(feature_names)

    model = cls.pruning(x[len(y)*8/10:], y[len(y)*8/10:], 1)
    model.draw_me(feature_names, 'after_pruning')


def parse_args():
    parser = argparse.ArgumentParser(description='Experiments with decision trees')
    parser.add_argument('-o', dest='out_path', help='a path to the exported tree')
    parser.add_argument('ds_path', nargs=1)
    return parser.parse_args()


if __name__ == "__main__":
    main()