import numpy

def add_to_dict(all_d, lst):
    lst_d = dict(map(lambda x: (x, 1), lst))
    lst_d_i = lst_d.items()
    all_d_i = all_d.items()
    arr1 = map(lambda x, y: (x[0], x[1]) if (x != None and x[0] not in [k for k,_ in all_d_i]) else (0, 0), lst_d_i, all_d_i)
    arr1 = filter(lambda x: x[0] != 0, arr1)
    arr2 = map(lambda x, y: (y[0], y[1])  if (y != None and y[0] not in [k for k,_ in lst_d_i]) else (y[0], y[1] + lst_d[y[0]])\
               if y != None else (0, 0), lst_d_i, all_d_i)
    arr2 = filter(lambda x: x[0] != 0, arr2)
    return dict(arr2 + arr1)

def create_men(men, women):
    men_i = men.items()
    women_i = women.items()
    arr1 = map(lambda x, y: (x[0], 1)\
        if (x != None and x[0] not in [k for k,_ in women_i]) else (0, 0), men_i, women_i)
    arr1 = filter(lambda x: x[0] != 0, arr1)
    arr2 = map(lambda x, y: (y[0], -1)  if (y != None and y[0] not in [k for k,_ in men_i])\
        else (y[0], (-y[1] + men[y[0]]) / float(y[1] + men[y[0]])) if y != None else (0, 0), men_i, women_i)
    arr2 = filter(lambda x: x[0] != 0, arr2)
    return dict(arr1 + arr2)

class GDAlgorithm:
    def __init__(self, theta = numpy.array([[1], [1], [5]]), alpha = 0.5, numIterations = 1000):
        self.theta = theta
        self.alpha = alpha
        self.numIterations = numIterations

    def gradient(self, X_train, y_train):
        #print 'fasolinka'
        #print X_train.shape
        #print y_train.shape
        #print self.theta.shape
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

        men = filter(lambda x: x != 0, map(lambda x, y: x if y == 2 else 0, X_train, y_train))
        women = filter(lambda x: x != 0, map(lambda x, y: x if y == 1 else 0, X_train, y_train))
        arr_men = numpy.array(map(lambda x: float(x), men[0][1]))
        for friend in men:
          arr_men = numpy.vstack((arr_men, numpy.array(map(lambda x: float(x), friend[1]))))
        arr_men = arr_men[1:]
        sum_men = numpy.sum(arr_men, axis=0)

        arr_women = numpy.array(map(lambda x: float(x), women[0][1]))
        for friend in women:
          arr_women = numpy.vstack((arr_women, numpy.array(map(lambda x: float(x), friend[1]))))
        arr_women = arr_women[1:]
        sum_women = numpy.sum(arr_women, axis=0)
        arr_total = map(lambda x, y: float(float(x) - float(y)) / float(x + y) if (x != 0 or y != 0) else 0, sum_men, sum_women)

        arr_total = numpy.array(arr_total)
        arr_men = arr_men * arr_total
        arr_women = arr_women * arr_total
        arr_men = numpy.vstack((arr_men, arr_women))
        arr_men = numpy.sum(arr_men, axis=1)

        self.arr_total = arr_total
        self.group_titles = men[0][0]

        X_train = numpy.array([arr_men.transpose()])

        men_name = map(lambda friend: friend[2], men)
        women_name = map(lambda friend: friend[2], women)

        X_train = numpy.r_[X_train, numpy.array(men_name + women_name).transpose()]
        y_train = numpy.array([1] * len(men) + [-1] * len(women))
        X_train = numpy.r_[numpy.ones((1, X_train.shape[1])), X_train]

        for i in range(0, self.numIterations):
            self.theta = self.theta + self.alpha * gradient(self, X_train, y_train)

            #y_train_copy = y_train.reshape(y_train.shape[0], 1)

            #if all(self.predict(X_train) == y_train_copy):
            #    break
        return self

    def predict(self, X_test):
        test_matrix = self.arr_total
        header_test = X_test[0][0]
        header_train = self.group_titles
        d_train = {key:i for i, key in enumerate(header_train)}
        d_test = {key:i for i, key in enumerate(header_test)}
        h_train_len = len(header_train)
        for friend in X_test:
            d_test = {key:i for i, key in zip(friend[1], header_test)}
            friend_groups = numpy.zeros(h_train_len)
            indices = [d_train[group_name] for group_name in friend[0] if (group_name in d_train and d_test[group_name] != 0)]
            friend_groups[indices] = 1
            test_matrix = numpy.vstack((test_matrix, friend_groups))
        test_matrix = test_matrix[1:]

        test_matrix = test_matrix * self.arr_total
        test_sum = numpy.sum(test_matrix, axis=1)
        men_name = map(lambda friend: friend[2], X_test)
        X_test = numpy.array([test_sum.transpose()])
        X_test = numpy.r_[X_test, numpy.array(men_name).transpose()]
        X_test = numpy.r_[numpy.ones((1, X_test.shape[1])), X_test]
        cl_arr = numpy.dot(X_test.transpose(), self.theta)

        sgn_arr = numpy.ones(cl_arr.shape)
        sgn_arr[(cl_arr > 0)] = int(2)

        return sgn_arr.transpose()[0]



    def decision_function(self, x):
        x = numpy.r_[1, x]
        cl_arr = numpy.dot(x, self.theta)

        return cl_arr
