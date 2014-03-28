import numpy as np

def gradient(X_train, y_train, theta):
    #grad = np.sum(np.dot(np.dot(X_train.transpose(), theta).transpose(), y_train))
    margin = np.dot(np.dot(X_train.transpose(), theta).transpose(), y_train)
    negative_indices = np.ones(margin.shape)
    negative_indices[(margin > 0)] = 0
    #X_train * np.tile(y_train, (1, X_train.shape[1]))
    #grad = np.dot(X_train.transpose(), theta)
    grad = np.sum(X_train * np.tile(y_train, (1, X_train.shape[1])) * np.tile(negative_indices, (1, X_train.shape[1])), axis = 1)
    grad = grad.reshape(X_train.shape[0], 1)
    return grad

def gradientDescent(X_train, y_train, theta, alpha, gradient, numIterations = 1000):
    for i in range(0, numIterations):
        theta -= alpha * gradient(X_train, y_train, theta)
    return theta

def classifier(X_test, theta):
    cl_arr = np.dot(X_test.transpose(), theta)
    sgn_arr = np.ones(cl_arr.shape)
    sgn_arr[(cl_arr < 0)] = -1
    sgn_arr[(cl_arr == 0)] = 0
    return sgn_arr
