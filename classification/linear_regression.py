__author__ = 'vludv'

import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.metrics import mean_absolute_error
import datetime
import re

class FbLinRegVectorizer:
    """
    convert raw facebook user's data to numpy arrays
    """

    def __init__(self):
        self.feature_names = None

    def fit_transform(self, X, target_feature="age"):
        """
        input: X - array of facebook user dicts
        output: A, b
                A - numpy array of feature vectors
                b - numpy array of target values
        """
        X_dst = []
        y_dst = []
        for user_fb_raw in X:
            learn_features = self.extract_learn_data(user_fb_raw)
            target = learn_features.get(target_feature)
            if target is None or target > 80:
                continue
            vec = self.get_user_vector(learn_features)
            X_dst.append(vec)
            y_dst.append(float(target))

        svectorizer = DictVectorizer()
        X_dst = svectorizer.fit_transform(X_dst).toarray()
        X_dst = np.nan_to_num(X_dst)
        y_dst = np.array(y_dst)
        self.feature_names = svectorizer.get_feature_names()

        return X_dst, y_dst

    def get_feature_names(self):
        return self.feature_names

    def get_user_vector(self, user):
        vec = {}
        #correlation between age and (sex and relationship)
        vec["sex"] = user.get("sex")
        self.empty_proc(user, vec, "relationship")
        #obiviously correlation between age and becoming employee year
        self.empty_proc(user, vec, "first_work")
        #obiviously correlation between graduate year and age
        self.empty_proc(user, vec, "last_education")
        vec["one"] = 1
        return vec

    @staticmethod
    def empty_proc(dict_src, dict_dst, key):
        """
        replace pair in source dict by two pairs in destination dict:
            first - None flag
            second - original value (if it is not None)
        """
        v = dict_src.get(key)
        if v is None:
            dict_dst["empty_" + key] = 1
            dict_dst[key] = 0
        else:
            dict_dst["empty_" + key] = 0
            dict_dst[key] = v

    @staticmethod
    def extract_learn_data(user):
        return {
            "age"           : FbLinRegVectorizer.parse_date(user.get("birthday")),
            "sex"           : user.get("sex"),
            "relationship"  : user.get("relationship_status"),
            "first_work"    : FbLinRegVectorizer.extract_first_work_year(user),
            "last_education": FbLinRegVectorizer.extract_last_education_year(user)
        }

    @staticmethod
    def extract_last_education_year(user):
        works = user.get("education")
        if works:
            today_year = datetime.date.today().year
            edu_years = []
            for cur_edu in works:
                if cur_edu.get("type") == "College" and cur_edu.get("year") and cur_edu.get("year").get("name"):
                    year = int(cur_edu.get("year").get("name"))
                    if today_year - year < 100:
                        edu_years.append(today_year - year)
            if edu_years:
                return min(edu_years)
        return None

    @staticmethod
    def extract_first_work_year(user):
        works = user.get("work")
        if works:
            works_years = []
            for cur_work in works:
                year_start = FbLinRegVectorizer.parse_date(cur_work.get("start_date"))
                if not year_start is None:
                    works_years.append(year_start)
            if works_years:
                return max(works_years)
        return None

    @staticmethod
    def parse_date(date_str):
        if date_str:
            parts = re.split("[/-]", date_str)
            if len(parts) == 3:
                if date_str.find("/") > 0:
                    date = datetime.date(int(parts[2]), int(parts[0]), int(parts[1]))
                else:
                    date = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                years = float((date.today() - date).days / 365.2425)
                return years
        return None

class LinearRegression:

    def __init__(self):
        self.method = "Gradient Descent"
        self.metric = "L2"
        self.A = None
        self.b = None
        self.train_coefs = None

    #sklearn-like interface
    def get_params(self, deep=True):
        return {}

    #sklearn-like interface
    def set_params(self, **params):
        pass

    def fit(self, A, b):
        assert A.ndim == 2 and b.ndim == 1 and A.shape[0] == b.shape[0]

        self.num_smaples = A.shape[0]
        self.num_features = A.shape[1]
        self.A = np.array(A, dtype=np.float64)
        self.b = np.array(b, dtype=np.float64)

        self.train_coefs = self.gradient_descent()
        return self.train_coefs

    def predict(self, A):
        assert A.ndim == 2 and A.shape[1] == self.num_features and not self.train_coefs is None
        return np.dot(A, self.train_coefs)

    def predict_proba(self, x):
        raise NotImplementedError()

    def gradient_descent(self, start=None, reps=0.001, max_iters=1000):
        """
        quickest gradient descent realization
        """

        if start is None:
            start = np.zeros(self.num_features)
        iteration = 0
        cur_pos = start.copy()
        step = np.zeros(self.num_features)
        eps = reps * self.num_features

        while iteration < max_iters:
            grad = self.functional_L2_grad(cur_pos)
            grad_len = np.linalg.norm(grad)

            if grad_len < eps and np.linalg.norm(step) < eps:
                break

            #compute optimal coefficient for gradient
            d = self.cur_error
            g = np.dot(self.A, grad)
            alpha_optimal = np.dot(d, g)/np.dot(g, g)

            step = alpha_optimal * grad
            cur_pos -= step
            iteration += 1

        #print "iterations:", iteration

        return cur_pos

    def functional_L2(self, x):
        self.cur_error = np.dot(self.A, x) - self.b
        return np.dot(self.cur_error, self.cur_error)

    def functional_L2_grad(self, x):
        self.cur_error = np.dot(self.A, x) - self.b
        return 2*np.dot(self.cur_error, self.A)

def linear_algebra_test():
    dim = 1000
    A = np.identity(dim) + np.random.sample((dim, dim))/2.0
    b = np.random.sample((dim,))

    lr = LinearRegression()
    lr.fit(A, b)
    b_est = lr.predict(A)
    print "Relative SSE=", np.linalg.norm(b_est - b) / dim

if __name__ == "__main__":
    linear_algebra_test()