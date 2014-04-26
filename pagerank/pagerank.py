# coding=utf-8
import numpy
import numpy.linalg
import sklearn.preprocessing

__author__ = 'nikolayanokhin'

EPSILON = 1e-6


def pagerank(m, beta):
    n, p = m.shape
    if n != p:
        raise ValueError("M is not square transition matrix")

    m_norm = sklearn.preprocessing.normalize(m, axis=0, norm='l1')
    m_beta = beta * m_norm
    teleport = numpy.ones(n) / n * (1 - beta)

    v = numpy.ones(n) / n
    while True:
        v1 = pagerank_iteration(v, m_beta, teleport)
        if numpy.linalg.norm(v1 - v, numpy.inf) < EPSILON:
            break
        v = v1
    return v


def pagerank_iteration(v, m_beta, teleport):
    return numpy.dot(m_beta, v) + teleport


def main():
    print "Welcome to the PageRank calculator"

    # Группа 1
    # m = numpy.array([
    #     [45, 30, 40, 25],
    #     [20, 15, 20, 10],
    #     [20, 30, 25, 25],
    #     [15, 25, 15, 20]
    # ], dtype=float)

    # Группа 2
    # m = numpy.array([
    #     [45, 40, 40, 40],
    #     [20, 20, 22, 20],
    #     [20, 25, 21, 20],
    #     [15, 15, 17, 20]
    # ], dtype=float)

    # Группа 3
    # m = numpy.array([
    #     [30, 30, 30],
    #     [30, 30, 40],
    #     [30, 30, 20]
    # ], dtype=float)

    # Группа 4
    m = numpy.array([
        [30, 40, 30, 30],
        [20, 20, 20, 20],
        [30, 20, 20, 20],
        [10, 20, 30, 30]
    ], dtype=float)

    # Группа 6
    # m = numpy.array([
    #     [33, 33, 34],
    #     [33, 34, 33],
    #     [34, 33, 33]
    # ], dtype=float)

    pr = pagerank(m, 0.9)
    print "Computed pagerank for matrix\n{}\nPageRank={}".format(m, pr * 38)


if __name__ == "__main__":
    main()
