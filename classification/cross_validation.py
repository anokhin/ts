import argparse
import sys
import random
import numpy

from naive_bayes import GaussianNB
from predict import CONVERSION_FUNCTIONS, FEATURE_FIELDS, FRIENDS_INDEX
from tsv_import import get_data_from_file, get_friends, determine_intervals
from tsv_import import break_on_intervals
from naive_bayes import prediction_score


def choose_random_items(data, results, amount):
    """Randomly chooses amount samples from data and results
    Returns randomly chosen and unchosen data and results separately
    """
    chosen_indexes = random.sample(range(len(data)), amount)
    chosen_data = []
    chosen_results = []
    unchosen_data = []
    unchosen_results = []
    for i in range(len(data)):
        if i in chosen_indexes:
            chosen_data.append(data[i])
            chosen_results.append(results[i])
        else:
            unchosen_data.append(data[i])
            unchosen_results.append(results[i])

    return chosen_data, chosen_results, unchosen_data, unchosen_results


def cross_val_score(classifier_class, data, results, cv):
    return [
        prediction_score(
            classifier_class(),
            *choose_random_items(data, results, len(data) / cv),
            use_sklearn_nb=use_sklearn_nb
        )
        for i in range(cv)
    ]


def choose_random_items_with_friends(data, results, amount, friends):
    """Randomly chooses amount samples from data and results
    Returns randomly chosen and unchosen data and results separately
    """
    chosen_indexes = random.sample(range(len(data)), amount)
    chosen_data = []
    chosen_results = []
    chosen_friends = []
    unchosen_data = []
    unchosen_results = []
    for i in range(len(data)):
        if i in chosen_indexes:
            chosen_data.append(data[i])
            chosen_results.append(results[i])
            chosen_friends.append(friends[i])
        else:
            unchosen_data.append(data[i])
            unchosen_results.append(results[i])

    return chosen_data, chosen_results, unchosen_data, unchosen_results, \
        chosen_friends


def cross_val_regression_score(classifier_class, data, results, cv, friends):
    return [
        regression_score(
            classifier_class,
            *choose_random_items_with_friends(
                data, results, len(data) / cv, friends
            )
        )
        for i in range(cv)
    ]


def regression_score(
    classifier_class,
    data_to_predict, results_to_predict,
    data_to_train, training_results,
    friends_to_predict
):
    classifier = classifier_class()
    classifier.fit(data_to_train, training_results)

    predicted_results = [
        classifier.predict(sample) for sample in data_to_predict
    ]
    predicted_regression = [
        numpy.mean(predicted_result) for predicted_result in predicted_results
    ]
    square_differences = [
        (predicted - actual) ** 2
        for predicted, actual in zip(predicted_regression, friends_to_predict)
    ]
    return numpy.sqrt(numpy.mean(square_differences))


def main():
    parser = argparse.ArgumentParser(description='cross-validate data')
    parser.add_argument(
        '--data', action='store', metavar='FILE',
        help='Filename of tsv file with training data'
    )
    parser.add_argument(
        '--intervals', action='store', type=int,
        help='Amount of intervals of ages. If not provided, will use 2'
    )
    parser.add_argument(
        '--cv_groups', action='store', type=int,
        help='Amount of groups for cross-validation. If not provided, use 5'
    )
    args = parser.parse_args()
    tsv_filename = args.data
    intervals = args.intervals or 2
    amount_of_groups = args.cv_groups or 5
    if tsv_filename is None:
        print "Please provide tsv file"
        sys.exit(1)

    print "Feature fields: %s" % FEATURE_FIELDS

    data = get_data_from_file(
        tsv_filename,
        FEATURE_FIELDS,
        CONVERSION_FUNCTIONS
    )

    ages = get_friends(data, FEATURE_FIELDS)
    age_intervals = determine_intervals(
        intervals, ages
    )
    print "intervals: %s" % age_intervals
    age_classes = break_on_intervals(ages, age_intervals)
    numbers_of_intervals = dict(
        [(interval, i) for i, interval in enumerate(age_intervals)]
    )
    numbered_classes = [
        numbers_of_intervals[age_class] for age_class in age_classes
    ]

    # delete friends column from data
    for user in data:
        user.pop(FRIENDS_INDEX)

    scores = cross_val_regression_score(
        GaussianNB, data, age_classes, amount_of_groups, ages
    )
    print scores
    print "Mean score (of scores above):"
    print numpy.mean(scores)


if __name__ == '__main__':
    main()
