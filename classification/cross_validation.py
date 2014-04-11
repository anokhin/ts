import argparse
import sys
import random

from predict import CONVERSION_FUNCTIONS, FEATURE_FIELDS
from tsv_import import get_data_from_file, get_ages, determine_intervals
from tsv_import import break_on_intervals
from naive_bayes import GaussianNB, prediction_score


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
            *choose_random_items(data, results, len(data) / cv)
        )
        for i in range(cv)
    ]


def main():
    parser = argparse.ArgumentParser(description='cross-validate data')
    parser.add_argument(
        '--data', action='store', metavar='FILE',
        help='Filename of tsv file with training data'
    )
    parser.add_argument(
        '--intervals', action='store', type=int,
        help='Amount of intervals of ages. If not provided, will use 5'
    )
    parser.add_argument(
        '--cv_groups', action='store', type=int,
        help='Amount of groups for cross-validation. If not provided, use 5'
    )
    args = parser.parse_args()
    tsv_filename = args.data
    intervals = args.intervals or 5
    amount_of_groups = args.cv_groups or 5
    if tsv_filename is None:
        print "Please provide tsv file"
        sys.exit(1)

    data = get_data_from_file(
        tsv_filename,
        FEATURE_FIELDS,
        CONVERSION_FUNCTIONS
    )

    ages = get_ages(data, FEATURE_FIELDS)
    age_intervals = determine_intervals(
        intervals, ages
    )
    age_classes = break_on_intervals(ages, age_intervals)

    scores = cross_val_score(
        GaussianNB, data, age_classes, amount_of_groups
    )
    print scores


if __name__ == '__main__':
    main()
