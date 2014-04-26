import argparse
import numpy
import numpy.random
from sklearn.cluster import Ward
import sklearn.datasets
import matplotlib.pylab as pylab

__author__ = 'nikolayanokhin'


def generate_data(n):
    print "Generating data set with %s clusters" % n
    centers = numpy.random.randint(20, size=(n, 2))
    return sklearn.datasets.make_blobs(n_samples=750, centers=centers, cluster_std=1)


def plot_data(x, labels):
    print "Plotting data set"
    for label in numpy.unique(labels):
        colors = pylab.cm.jet(numpy.float(label) / numpy.max(labels + 1))
        pylab.scatter(x[labels == label, 0], x[labels == label, 1], c=colors)


def plot_criterion(ks, crs, col):
    print "Plotting clustering criterion"
    pylab.plot(ks[1:], crs[1:], col + 'o-')


def squared_criterion(x, labels):
    u_labels = numpy.unique(labels)
    s = 0.0
    for label in u_labels:
        xl = x[labels == label, :]
        centroid = numpy.mean(xl, axis=0)
        s += numpy.sum((xl - centroid) * (xl - centroid))
    return s/len(u_labels)


def diameter_criterion(x, labels):
    u_labels = numpy.unique(labels)
    s = 0.0
    for label in u_labels:
        xl = x[labels == label, :]
        d = 0
        for x1 in xl:
            for x2 in xl:
                l = numpy.sqrt(numpy.sum((x1 - x2) * (x1 - x2)))
                if l > d:
                    d = l
        s += d
    return s/len(u_labels)


def silhouette_criterion(x, labels):
    # TODO: Implement silhouette criterion
    return len(numpy.unique(labels)) ** 2


def main():
    print "## Welcome to the clustering tutorial ##"
    args = parse_args()
    x, tc = generate_data(args.n)

    ks = numpy.arange(1, args.k + 1)
    crs = numpy.zeros(args.k)
    col = 'k'

    print "Computing %s clustering quality criterion" % args.criterion
    for j in xrange(args.k):
        ward = Ward(n_clusters=ks[j]).fit(x)
        labels = ward.labels_

        if args.criterion == 'squared':
            crs[j] = squared_criterion(x, labels)
            col = 'r'
        elif args.criterion == 'diameter':
            crs[j] = diameter_criterion(x, labels)
            col = 'g'
        elif args.criterion == 'silhouette':
            crs[j] = silhouette_criterion(x, labels)
            col = 'b'
        else:
            raise ValueError("Wrong criterion" + args.criterion)

    pylab.figure(figsize=(12, 6))

    ward = Ward(n_clusters=args.n).fit(x)
    labels = ward.labels_

    pylab.subplot(1, 2, 1)
    plot_data(x, labels)

    pylab.subplot(1, 2, 2)
    plot_criterion(ks, crs, col)

    pylab.show()


def parse_args():
    parser = argparse.ArgumentParser(description='Experiments with the number of clusters')
    parser.add_argument('-n', dest='n', type=int, default=3, help='the real number of clusters')
    parser.add_argument('-k', dest='k', type=int, default=10, help='the max number of clusters to test')
    parser.add_argument('-c', dest='criterion', choices=['squared', 'diameter', 'silhouette'])
    return parser.parse_args()


if __name__ == "__main__":
    main()
