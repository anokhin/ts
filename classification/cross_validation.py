import argparse
import sys
import random

from predict import CONVERSION_FUNCTIONS, FEATURE_FIELDS
from tsv_import import get_data_from_file, get_ages, determine_intervals
from tsv_import import break_on_intervals
from naive_bayes import GaussianNB


def choose_random_items(data, results, amount):
    """Returns random sample from data and its matching sample of results"""
    chosen_pairs = random.sample(zip(data, results), amount)
    return zip(*chosen_pairs)


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
    classifier = GaussianNB()

    scores = cross_validation.cross_val_score(
        classifier, data, age_classes, amount_of_groups
    )
    print scores


if __name__ == '__main__':
    main()
