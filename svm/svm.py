import argparse

import numpy
import pylab
import numpy.random
import sklearn.datasets


__author__ = 'Nikolay Anokhin'


def generate_linear(args):
    print "Generating 'Linearly-separated' data set"

    x = numpy.random.random((args.size, 2))
    y = numpy.zeros(args.size, dtype=int)
    noise = numpy.random.randn(args.size) * args.nl
    y[x[:, 1] - (args.k * x[:, 0] + args.b) > noise] = 1

    return x, y


def generate_concentric(args):
    print "Generating 'Concentric circles' data set"
    x = numpy.zeros((args.size, 2))
    x[:args.size/2, 0] = args.sigma * numpy.random.randn(args.size/2) + args.r1
    x[args.size/2:, 0] = args.sigma * numpy.random.randn(args.size/2) + args.r2
    x[:, 1] = (numpy.random.random(args.size) - 0.5) * 2 * numpy.pi
    y = numpy.hstack([numpy.zeros(args.size/2, dtype=int), numpy.ones(args.size/2, dtype=int)])

    z = numpy.zeros((args.size, 2))
    z[:, 0] = x[:, 0] * numpy.cos(x[:, 1])
    z[:, 1] = x[:, 0] * numpy.sin(x[:, 1])

    return z, y


def generate_gauss(args):
    print "Generating 'Gaussian mixture' data set"

    x, y = sklearn.datasets.make_classification(n_samples=args.size,
                                                n_features=2,
                                                n_informative=2,
                                                n_redundant=0,
                                                n_classes=2,
                                                n_clusters_per_class=2)
    return x, y


def generate_sin(args):
    print "Generating 'Sinus-separated' data set"

    x = numpy.random.random((args.size, 2))
    x[:, 0] = x[:, 0] * 4 * numpy.pi
    x[:, 1] = (x[:, 1] - 0.5) * 2
    y = numpy.zeros(args.size, dtype=int)
    y[x[:, 1] > numpy.sin(x[:, 0])] = 1

    return x, y


def plot_data_set(x, y, description=''):
    pylab.figure(figsize=(10, 10))

    colors = numpy.array(['r', 'b'])[y]
    pylab.title(description, fontsize='small')
    pylab.scatter(x[:, 0], x[:, 1], marker='o', c=colors, s=50)

    pylab.show()


def main():
    print "## Welcome to the Text Mining tutorial ##"
    args = parse_args()

    x, y = args.func(args)

    plot_data_set(x, y)


def parse_args():
    parser = argparse.ArgumentParser(description='SVM tutorial')
    parser.add_argument('-s', dest='size', type=int, default=100)

    subparsers = parser.add_subparsers(help='data set type. Choose one of: "lin", "cc", "gauss", "sin"')

    parser_lin = subparsers.add_parser('lin', help='Data set for linear separation')
    parser_lin.add_argument('-k', dest='k', type=float, default=1.0, help='Separator slope')
    parser_lin.add_argument('-b', dest='b', type=float, default=0.0, help='Separator intercept')
    parser_lin.add_argument('-n', dest='nl', type=float, default=0.1, help='Noise level')
    parser_lin.set_defaults(func=generate_linear)

    parser_cc = subparsers.add_parser('cc', help='Data set with concentric circles')
    parser_cc.add_argument('-1', dest='r1', type=float, default=1.0, help='First radius')
    parser_cc.add_argument('-2', dest='r2', type=float, default=2.0, help='Second radius')
    parser_cc.add_argument('-s', dest='sigma', type=float, default=0.3, help='Noise blur')
    parser_cc.set_defaults(func=generate_concentric)

    parser_gauss = subparsers.add_parser('gauss', help='Data set with gaussian mixtures')
    parser_gauss.set_defaults(func=generate_gauss)

    parser_sin = subparsers.add_parser('sin', help='Data set with sinus separator')
    parser_sin.set_defaults(func=generate_sin)

    return parser.parse_args()


if __name__ == "__main__":
    main()
