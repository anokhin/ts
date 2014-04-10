import numpy


class GaussianNB:
    def fit(self, samples, results):
        """Arguments:
            samples - list of lists, each sublist has the same length and
            contains values of features.

            results - list of classes, one for each sample in samples,
            in the same order. Each value here must first be added with
            add_classes method.
        """
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
        self.__classes = classes
