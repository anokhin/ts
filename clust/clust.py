import argparse

import numpy
import pylab
import numpy.random
import sklearn.datasets


__author__ = 'Nikolay Anokhin'


class IterativeClustering(object):
    """
    A basic (unoptimised) clustering algorithm,
    using an optimality criterion to select clustering.
    """

    def __init__(self, n_classes, convergence_count=1000, max_iterations=int(1e+6)):
        self.n_classes = n_classes
        self.convergence_count = convergence_count
        self.max_iterations = max_iterations

    def fit_predict(self, x):
        """
        Cluster the input data set x and return
        cluster assignments.
        """
        # TODO: Solve optimization locality problem
        y = numpy.random.randint(0, self.n_classes, size=x.shape[0])
        j = self.j(x, y)

        convergence = 0
        for i in xrange(self.max_iterations):
            k = numpy.random.randint(x.shape[0])

            c_best = y[k]
            convergence += 1
            for c in xrange(self.n_classes):
                y[k] = c
                j_curr = self.j(x, y)
                if j_curr < j:
                    convergence = 0
                    c_best = c
                    j = j_curr
            y[k] = c_best

            if convergence > self.convergence_count:
                print "Converged at iteration {}".format(i)
                break

        return y

    def j(self, x, y):
        """
        A simple quadratic criterion.
        """
        # TODO: Implement transformation-invariant criterion
        result = 0

        for c in xrange(self.n_classes):
            x_c = x[y == c, :]
            mean = numpy.mean(x_c, axis=0)
            for x_i in x_c:
                result += ((x_i - mean)**2).sum()

        return result


COLORS = numpy.array(['r', 'g', 'b', 'm'])
MARKERS = numpy.array(['o', 's', 'v', 'D'])


def transform_data_set(x, a, b):
    """
    Apply z = Ax + b linear transformation matrix to the data set x
    """
    z = numpy.dot(a, x.transpose()).transpose() + b
    return z


def generate_gauss(args):
    print "Generating 'Gaussian mixture' data set"

    x, y = sklearn.datasets.make_classification(n_samples=args.size,
                                                n_features=2,
                                                n_informative=2,
                                                n_redundant=0,
                                                n_classes=args.classes,
                                                n_clusters_per_class=1)
    return x, y


def plot_data_set(x, y_true, y_clust):
    for y in numpy.unique(y_true):
        x_true = x[y_true == y, :]
        marker = MARKERS[y]
        colors = COLORS[y_clust[y_true == y]]
        pylab.scatter(x_true[:, 0], x_true[:, 1], marker=marker, c=colors, s=50)


def plot_centroids(x, y_clust):
    for y in numpy.unique(y_clust):
        x_c = x[y_clust == y, :]
        mean = numpy.mean(x_c, axis=0)
        pylab.scatter(mean[0], mean[1], marker='*', c=COLORS[y], s=400)


def main():
    print "## Welcome to the Text Mining tutorial ##"
    args = parse_args()

    x, y_true = generate_gauss(args)

    model = IterativeClustering(args.classes)
    y_clust = model.fit_predict(x)

    pylab.figure(figsize=(12, 6))

    # Plot clustering of the original data set
    pylab.subplot(1, 2, 1)
    plot_data_set(x, y_true, y_clust)
    plot_centroids(x, y_clust)

    # Apply scaling transformation
    # TODO: Try rotation, shift and general linear
    a = numpy.array([[4, 0], [0, 1]])
    b = numpy.array([0, 0])
    z, v_true = transform_data_set(x, a, b), y_true
    v_clust = model.fit_predict(z)

    # Plot clustering of the transformed data set
    pylab.subplot(1, 2, 2)
    plot_data_set(z, v_true, v_clust)
    plot_centroids(z, v_clust)

    pylab.show()


def parse_args():
    parser = argparse.ArgumentParser(description='Clustering tutorial')
    parser.add_argument('-s', dest='size', type=int, default=10)
    parser.add_argument('-c', dest='classes', type=int, default=2)
    args = parser.parse_args()

    if args.classes > len(COLORS):
        raise ValueError('At most {} classes supported'.format(len(COLORS)))

    return args


if __name__ == "__main__":
    main()
