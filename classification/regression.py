__author__ = 'vludv'

import numpy as np

def gradientDescent(func, derivative, start, grad_coef = 1.0, eps = 0.0001, max_iters = 1000):
    iteration = 0
    cur_pos = start.copy()
    step = np.zeros(start.shape)

    while iteration < max_iters:
        gradient = derivative(cur_pos)

        if np.linalg.norm(gradient) < eps and np.linalg.norm(step) < eps:
            break

        step = grad_coef * gradient
        cur_pos -= step
        iteration += 1

    return cur_pos

def linearRegression(x, y):
    """
    x - 2D numpy array of objects, one object per row
    y - 1D numpy array of values corresponding objects in x
    return - 1D numpy array of computed coefficients
    """

    rows = x.shape[0]
    cols = x.shape[1]

    assert x.ndim == 2 and y.ndim == 1 and x.shape[0] == y.shape[0], "Incorrect dimensions of x and y"

    def sqrFunctional(x, A = x, b = y):
        return np.sum( (np.dot(A, x) - b)**2 )

    def sqrFunctionalDerivative(x, A = x, b = y):
        d = np.dot(A, x) - b
        return 2*np.dot(d, A)

    start = np.zeros(cols)
    decision = gradientDescent(sqrFunctional, sqrFunctionalDerivative, start, 0.5)
    return decision

def main():
    dim = 5
    A = np.identity(dim) + np.random.sample((dim, dim))/1000.0
    b = np.random.sample((dim,))

    x = linearRegression(A, b)

    print "x=", x
    print "Ax=", np.dot(A, x)
    print "b=", b
    print "SSE=", np.linalg.norm(np.dot(A, x) - b)

if __name__ == "__main__":
    main()