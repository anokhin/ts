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
    m = numpy.array([
        [50., 10., 30., 30.],
        [10., 70., 10., 5.],
        [20., 10., 30., 30.],
        [20., 10., 30., 35.]
    ])
    pr = pagerank(m, 0.9)
    print "Computed pagerank for matrix\n{}\nPageRank={}".format(m, pr)


if __name__ == "__main__":
    main()
