import StringIO
import argparse
import numpy
import scipy.stats
from sklearn import tree
from sklearn.cross_validation import cross_val_score
import sklearn.feature_extraction
from sklearn.tree import DecisionTreeClassifier
import pydot

TARGET = "target"


def read_data_set(ds_path, columns):
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

            if row_valid and row and target:
                data.append(row)
                targets.append(target)

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


def fit_decision_tree(x, y):
    model = DecisionTreeClassifier(criterion="entropy", min_samples_leaf=1000, max_depth=2)

    scores = cross_val_score(model, x, y, cv=20)
    print "Model mean accuracy: {}".format(numpy.mean(scores))

    model.fit(x, y)
    return model


def export_model(model, out_path):
    dot_data = StringIO.StringIO()
    tree.export_graphviz(model, out_file=dot_data)
    graph = pydot.graph_from_dot_data(dot_data.getvalue())
    graph.write_pdf(out_path)


def parse_int(s):
    return int(s) if s != "-1" else None


def parse_string(s):
    return s if s != "-1" else None


def main():
    print "## Welcome to the decision trees tutorial ##"
    args = parse_args()

    columns = {
        "age": (4, parse_int),
        "gender": (5, parse_int),
        "education": (29, parse_string),
        TARGET: (54, parse_int)
    }
    x, y, feature_names = read_data_set(args.ds_path[0], columns)

    print_set_stats(x, y, feature_names)

    model = fit_decision_tree(x, y)

    if args.out_path:
        export_model(model, args.out_path)


def parse_args():
    parser = argparse.ArgumentParser(description='Experiments with decision trees')
    parser.add_argument('-o', dest='out_path', help='a path to the exported tree')
    parser.add_argument('ds_path', nargs=1)
    return parser.parse_args()


if __name__ == "__main__":
    main()