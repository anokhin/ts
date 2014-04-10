class GaussianNB:
    def fit(self, samples, results):
        pass

    def predict(self, sample):
        pass

    def add_classes(self, classes):
        """Manually configure, how big the classes for our regression are,
        for example 0-10, 11-20, 21-30, etc.

        Arguments:
            classes - list of pairs, each pair corresponds to min and max
            values of that class (for example (0,10) corresponds to 0-10.
            Must not overlap, each next pair's values must be bigger than
            previous pair's values
        """
        pass
