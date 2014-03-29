__author__ = 'vludv'

import numpy as np

def gradientDescent(func, derivative, start, grad_coef=0.01, eps=0.001, max_iters=500):
    iteration = 0
    cur_pos = start.copy()
    step = np.zeros(start.shape)

    while iteration < max_iters:
        gradient = derivative(cur_pos)
        gradient_norm = np.linalg.norm(gradient)

        if gradient_norm < eps and np.linalg.norm(step) < eps:
            break

        #print "grad norm ", gradient_norm

        step = grad_coef / max(1, gradient_norm) * gradient
        cur_pos -= step
        iteration += 1

    return cur_pos

def linearRegression(A, b):
    """
    A - 2D numpy array of objects, one object per row
    b - 1D numpy array of values corresponding objects in x
    return - 1D numpy array of computed coefficients
    """
    cols = A.shape[1]

    assert A.ndim == 2 and b.ndim == 1 and A.shape[0] == b.shape[0], "Incorrect dimensions of x and y"

    A = np.array(A, dtype=np.float64)
    b = np.array(b, dtype=np.float64)

    def sqrFunctional(x):
        return np.sum( (np.dot(A, x) - b)**2 )

    def sqrFunctionalDerivative(x):
        d = np.dot(A, x) - b
        return 2*np.dot(d, A)

    start = np.zeros(cols, dtype=np.float64)
    decision = gradientDescent(sqrFunctional, sqrFunctionalDerivative, start)
    return decision

def linear_algebra_test():
    dim = 1000
    A = np.identity(dim) + np.random.sample((dim, dim))/2.0
    b = np.random.sample((dim,))

    x = linearRegression(A, b)

    #print "x=", x
    #print "Ax=", np.dot(A, x)
    #print "b=", b
    print "Relative SSE=", np.linalg.norm(np.dot(A, x) - b) / dim

if __name__ == "__main__":
    linear_algebra_test()