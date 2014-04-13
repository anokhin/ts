import sys
import numpy as np
from sklearn.preprocessing import LabelBinarizer
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.externals import six
from abc import ABCMeta


class BaseNB(six.with_metaclass(ABCMeta, BaseEstimator, ClassifierMixin)):

    def __init__(self):
        self.class_prior = None
        self.classes = None

    def predict(self, X):
        return self.classes[np.argmax(self._joint_likelihood(X), 1)]

    def predict_proba(self, X):
        jl = self._joint_likelihood(X)
        # normalize probability
        norm_coef = np.sum(jl, 1)[:, np.newaxis]
        jl = np.divide(jl, norm_coef)
        return jl[:]


    def predict_log_proba(self, X):
        return np.log(self.predict_proba(X))


class GaussianNB(BaseNB):

    def __init__(self):
        self.mean = None
        self.variance = None


    def fit(self, X, y):
        X = np.array(X, dtype = np.float128)
        y = np.array(y)
        samples, self.n_features = X.shape

        lb = LabelBinarizer()
        lb.fit(y)
        self.classes = lb.classes_
        self.n_class = self.classes.size

        # we'll find mean and variance using maximum likelihood estimation
        self.mean = np.array(np.zeros([self.n_class, self.n_features]), dtype=np.float128)
        self.variance = np.array(np.zeros([self.n_class, self.n_features]), dtype = np.float128)
        self.class_prior = np.zeros(self.n_class)


        EPS = 0.001
        for i, y_i in enumerate(self.classes):
            # get Xs only for y_i class
            X_yi = X[y == y_i]
            self.class_prior[i] = 1.0 * X_yi.size / X.size
            self.mean[i] = np.mean(X_yi, axis=0)
            self.variance[i] = np.array(np.var(X_yi, axis=0) + EPS, dtype=np.float128)
        return self


    def _joint_likelihood(self, X):
        likelihood = []
        samples, features = X.shape

        # calculate sample probabilities
        for i in range(0, self.classes.size):
            proba = self.class_prior[i] / np.prod(np.sqrt(2 * np.pi * self.variance[i])) * np.exp( -0.5 * np.sum(((X - self.mean[i]) ** 2) /
                                                                                                                 (self.variance[i]), 1))



            likelihood.append(proba)

        # work bad on big data, because variance and mean are very little
        likelihood = np.array(likelihood).T
        return likelihood


class BaseDiscreteNB(BaseNB):

    def __init__():
        self.classes = None
        self.n_class = None
        self.n_features = None
        self.feature_proba = None
        self.class_prior = None

    def fit(self, X, y):
        X = np.array(X)
        y = np.array(y)
        samples, self.n_features = X.shape

        # because our space of targets are discrete
        lb = LabelBinarizer()
        lb.fit(y)
        self.classes = lb.classes_
        self.n_class = self.classes.size

        self.class_prior = np.zeros(self.n_class, dtype=np.float64)
        self.feature_proba = []

        for i, y_i in enumerate(self.classes):
            # get Xs only for y_i class
            X_yi = X[y == y_i]
            class_count = X_yi[:, 0].size
            self.class_prior[i] = np.float64(class_count) / samples

            count_all_features = 0
            all_features = np.zeros(self.n_features)
            for sample_features in X_yi:
                # accumulate feature according our algorithm
                all_features, count_all_features = self._add_features_dens(
                    sample_features, all_features, count_all_features)

            # calculate probabilites according our algorithm
            self.feature_proba.append(
                self._compute_proba(all_features, count_all_features))

        return self


class MultinomialNB(BaseDiscreteNB):

    def __init__(self, alpha=1.0):
        self.alpha = alpha

    def _add_features_dens(self, sample_features, all_features, count_features):
        count_features += np.sum(sample_features)
        all_features += sample_features
        return all_features, count_features

    def _compute_proba(self, all_features, count_features):
        all_features += self.alpha
        return all_features / (count_features + self.alpha * self.n_class)

    def _joint_likelihood(self, X):
        X = np.array(X)
        # if X is 1-d array, we should interpret it like 2-d array
        if len(X.shape) == 1:
            X = X[np.newaxis, :]

        likelihood_all = []
        likelihood_x = np.zeros(self.n_class)
        for j in X:
            for i, y_i in enumerate(self.classes):
                proba = self.class_prior[i]
                for first, second in zip(j, self.feature_proba[i]):
                    # if feature is represented in a vector 
                    if not np.equal(first, 0.0):
                        proba *= first * second
                likelihood_x[i] = proba

            likelihood_all.append(likelihood_x.copy())

        return likelihood_all


class BernoulliNB(BaseDiscreteNB):

    def __init__(self, alpha=1.0):
        self.alpha = alpha

    def _add_features_dens(self, sample_features, all_features, count_features):
        binary_features = np.minimum(sample_features, 1.0)
        count_features += 1
        all_features = np.add(all_features, binary_features)
        return all_features, count_features

    def _compute_proba(self, all_features, count_features):
        all_features += self.alpha
        return all_features / (count_features + self.alpha * self.n_class)

    def _joint_likelihood(self, X):
        # if X is 1-d array, we should interpret it like 2-d array
        if len(X.shape) == 1:
            X = X[np.newaxis, :]

        likelihood_all = []
        likelihood_x = np.zeros(self.n_class)
        for j in X:
            for i, y_i in enumerate(self.classes):
                proba = self.class_prior[i]
                for first, second in zip(j, self.feature_proba[i]):
                    # if feature is represented in a vector, otherwise multiply with (1 - prob(feature_in_class))
                    if not np.equal(first, 0.0):
                        proba *= second
                    else:
                        proba *= (1 - second)
                likelihood_x[i] = proba

            likelihood_all.append(likelihood_x.copy())

        return likelihood_all
