import numpy

class GDAlgorithm:
    def __init__(self, theta = numpy.array([[5], [1], [5]]), alpha = 0.5, numIterations = 1000):
        self.theta = theta
        self.alpha = alpha
        self.numIterations = numIterations

    def gradient(self, X_train, y_train):

        margin = numpy.dot(X_train.transpose(), self.theta).transpose() * y_train

        negative_indices = numpy.ones(margin.shape)
        negative_indices[(margin > 0)] = 0

        y_modified = numpy.tile(y_train, (X_train.shape[0], 1))

        ones_theta_zero = numpy.ones((1, y_modified.shape[1]))

        y_modified[0] = -ones_theta_zero[0]

        grad = numpy.sum(X_train * y_modified * numpy.tile(negative_indices, (X_train.shape[0], 1)), axis = 1)
        grad = grad.reshape(X_train.shape[0], 1)

        return  grad

    def fit(self, X_train, y_train, gradient = gradient):
        X_train = numpy.r_[numpy.ones((1, X_train.shape[1])), X_train]

        for i in range(0, self.numIterations):
            self.theta = self.theta + self.alpha * gradient(self, X_train, y_train)

            y_train_copy = y_train.reshape(y_train.shape[0], 1)

            if all(self.predict(X_train) == y_train_copy):
                break

    def predict(self, X_test):
        cl_arr = numpy.dot(X_test.transpose(), self.theta)

        sgn_arr = numpy.ones(cl_arr.shape)
        sgn_arr[(cl_arr < 0)] = -1

        return sgn_arr



    def decision_function(self, x):
        x = numpy.r_[1, x]
        cl_arr = numpy.dot(x, self.theta)

        return cl_arr
