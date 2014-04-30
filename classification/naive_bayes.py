import numpy
from math import e
from math import sqrt
from math import pi


class GaussianNB:
    def fit(self, samples, results):
        """Arguments:
            samples - list of lists, each sublist has the same length and
            contains values of features.

            results - list of classes, one for each sample in samples,
            in the same order. Each value here must first be added with
            add_classes method.
        """
        self.__classes = sorted(list(set(results)))
        self.__check_classes(results)
        assert len(samples) == len(results)
        self.__class_prior_probabilities = {
            _class: 0.0 for _class in self.__classes}
        for result in results:
            self.__class_prior_probabilities[result] += 1.0 / len(results)

        # calculate mean and variance of each feature for each class
        total_features = len(samples[0])
        self.__means = {}
        self.__variances = {}
        for _class in self.__classes:
            samples_of_this_class = [
                sample for sample, result in zip(samples, results)
                if result == _class]

            for feature_index in range(total_features):
                feature_values = [
                    sample[feature_index] for sample in samples_of_this_class]
                self.__means[(_class, feature_index)] = numpy.mean(
                    feature_values)
                self.__variances[(_class, feature_index)] = gaussian_variance(
                    feature_values)

        return self

    def __check_classes(self, results):
        for result in results:
            if result not in self.__classes:
                raise Exception("{} - no such class".format(result))

    def predict(self, sample):
        predicted_log_probabilities = {
            numpy.log(self.__class_prior_probabilities[_class]) +
            numpy.sum([
                GaussianNB.__gaussian_likelihood_log(
                    value,
                    self.__means[(_class, index)],
                    self.__variances[(_class, index)]
                )
                for value, index in zip(sample, range(len(sample)))
            ]):
            _class
            for _class in self.__classes
        }
        return predicted_log_probabilities[
            max(predicted_log_probabilities.keys())
        ]

    @staticmethod
    def __gaussian_likelihood_log(value, mean, variance):
        if value is None:
            return np.log(1)

        result = -0.5 * numpy.log(2 * numpy.pi * variance)
        result -= (value - mean) ** 2 / (2 * variance)
        return result


def gaussian_variance(numbers):
    mean = numpy.mean(numbers)
    squared_differences = (numbers - mean) ** 2
    return sum(squared_differences) / len(numbers)


def prediction_score(
    classifier,
    data_to_predict, prediction_correct_results,
    data_to_train, training_results,
    use_sklearn_nb = False
):
    if use_sklearn_nb:
        data_to_predict = numpy.array(data_to_predict)
        prediction_correct_results = numpy.array(prediction_correct_results)
        data_to_train = numpy.array(data_to_train)
        training_results = numpy.array(training_results)
    classifier.fit(data_to_train, training_results)
    predicted_results = [
        classifier.predict(sample) for sample in data_to_predict
    ]
    matched_results = [
        True for correct, predicted
        in zip(prediction_correct_results, predicted_results)
        if correct == predicted
    ]
    return float(len(matched_results)) / float(len(data_to_predict))
