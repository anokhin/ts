from math import log

class Node:
    def __init__(self, is_leaf, probs, question):
        self.leaf = is_leaf
        self.left = self.right = None
        if is_leaf:
            self.probs = probs
        else:
            self.question = question

class ClassificationTree:
    @staticmethod
    def calc_probabilities(target):
        probs = dict()
        for t in target:
            if t not in probs:
                probs[t] = 1
            else:
                probs[t] += 1
        length = len(target) * 1.0
        for p in probs:
            probs[p] = probs[p] / length
        return probs

    @staticmethod
    def impurity_gini(target):
        probs = ClassificationTree.calc_probabilities(target)
        res = 1
        for p in probs.values():
            res -= p * p
        return res

    @staticmethod
    def impurity_enthropy(target):
        probs = ClassificationTree.calc_probabilities(target)
        res = 0
        for p in probs.values():
            res += p * log(p, 2)
        return -res

    @staticmethod
    def normalize_sample(sample):
        ''' substitute None with 'None', True with 1, False with 0,
        so we have only categories and numbers'''
        for feature in sample:
            if type(feature) == type(None):
                feature = 'None'
            elif type(feature) == type(False):
                feature = int(feature)
        return sample

    @staticmethod
    def impurity_misclass(target):
        probs = ClassificationTree.calc_probabilities(target)
        return 1 - max(probs.values())

    @staticmethod
    def move(v, sample):
        ''' decides which way (left or right) from v we must go
        based on sample'''
        n, val = v.question
        if type(val) == type('1'):
            return v.left if sample[n] == val else v.right
        else:
            return v.left if sample[n] <= val else v.right

    @staticmethod
    def divide(samples, question, target):
        ''' divides samples into 2 subsequences based on question
         of form [#feature, value]. 
         If value is str, then it's leave-one-out, otherwise threshold.
         Returns the resulting parts in form
         (left_samples, left_target, right_samples, right_target)'''
        n, value = question
        indicies = range(len(samples))
        if type(value) == type('1'):
            left = filter(lambda x: samples[x][n] == value, indicies)
            right = filter(lambda x: samples[x][n] != value, indicies)
        else:
            left = filter(lambda x: samples[x][n] <= value, indicies)
            right = filter(lambda x: samples[x][n] > value, indicies)
        r = lambda it, ind: [it[i] for i in ind]
        return (r(samples, left), r(target, left), r(samples, right), r(target, right))

    impurity_methods = dict([('gini', impurity_gini), ('entropy', impurity_enthropy), ('misclass', impurity_misclass)])

    def __init__(self, impurity_type='gini', size_threshold=1, delta_impurity_min=0):
        if size_threshold < 1 or delta_impurity_min < 0:
            print 'Incorrect thresholds!'
            raise ValueError
        self.size_threshold = size_threshold
        self.delta_impurity_min = delta_impurity_min
        if impurity_type not in ClassificationTree.impurity_methods:
            print 'Impurity method ' + impurity_type + ' not found!'
            print 'Available methods are: ' + ', '.join(ClassificationTree.impurity_methods.keys())
            raise ValueError
        self.impurity_function = ClassificationTree.impurity_methods[impurity_type].__func__
        self.root = None
    
    def fit(self, samples, target):
        ''' Takes training set  of size [n_samples * n_features], target function and makes a tree
        The abscence of some feature is treated as a new class 'None'. Boolean features are converted
        to numbers.
        Therefore, we have only string ot int features.
        '''
        for sample in samples:
            sample = ClassificationTree.normalize_sample(sample)
        self.root = self.make_tree(samples, target)

    def predict(self, x):
        x = ClassificationTree.normalize_sample(x) 
        probs = self.prob_predict(x)
        val, cl = -1, None
        for clas, prob in probs.items():
            if prob > val:
                val, cl = prob, clas
        return cl
    
    def prob_predict(self, x):
        cur = self.root
        while not cur.leaf:
            cur = ClassificationTree.move(cur, x)
        return cur.probs

    def make_tree(self, samples, target):
        length = len(target)
        if length <= self.size_threshold:
            return Node(True, ClassificationTree.calc_probabilities(target), None)
        else:
            max_delta, best_question = -200, None
            for n_question in range(len(samples[0])):
                values = sorted(set([samples[i][n_question] for i in range(length)]))
                for value in values:
                    left_samples, left_target, right_samples, right_target = ClassificationTree.divide(samples, (n_question, value), target) 
                    wleft = (len(left_samples) * 1.0) / length
                    delta = self.impurity_function(target) - wleft * self.impurity_function(left_target)
                    delta -= (1.0 - wleft) * self.impurity_function(right_target)
                    if delta > max_delta:
                        max_delta, best_question = delta, (n_question, value)

            left_samples, left_target, right_samples, right_target = ClassificationTree.divide(samples, best_question, target) 
            if max_delta <= self.delta_impurity_min:
                return Node(True, ClassificationTree.calc_probabilities(target), None)
            else:
                ret = Node(False, None, best_question)
                ret.left = self.make_tree(left_samples, left_target)
                ret.right = self.make_tree(right_samples, right_target)
                return ret

            

