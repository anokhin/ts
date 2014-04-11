import argparse
import sys

import tsv_import
import naive_bayes

from tsv_import import str_to_int_or_none
from tsv_import import identity


CONVERSION_FUNCTIONS = {
    u'firstname': identity,
    u'lastname': identity,
    u'\ufeffid': str_to_int_or_none,
    u'gender': str_to_int_or_none,
    u'relationships': str_to_int_or_none,
    u'status': str_to_int_or_none,
    u'wall': str_to_int_or_none,
    u'subscriptions': str_to_int_or_none,
    u'photos': str_to_int_or_none,
    u'friends': str_to_int_or_none
}

FEATURE_FIELDS = [
    u'gender', u'relationships', u'status', u'wall',
    u'subscriptions', u'photos', u'friends'
]


def load_training_data(tsv_filename, amount_of_intervals, classifier_class):
    user_lists = tsv_import.get_data_from_file(
        tsv_filename,
        FEATURE_FIELDS,
        CONVERSION_FUNCTIONS
    )
    ages = tsv_import.get_friends(user_lists, FEATURE_FIELDS)
    age_intervals = tsv_import.determine_intervals(
        amount_of_intervals, ages
    )
    age_classes = tsv_import.break_on_intervals(ages, age_intervals)
    classifier = classifier_class()
    classifier.fit(user_lists, age_classes)
    return age_intervals, user_lists, classifier


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Predict age for chosen ids')
    parser.add_argument(
        '--predict',
        action='store', metavar='FILE',
        help='Filename of tsv file with vk users to classify')
    parser.add_argument(
        '--train', action='store', metavar='FILE',
        help='Filename of tsv file with training data'
    )
    parser.add_argument(
        '--intervals', action='store', type=int,
        help='Amount of intervals of ages. If not provided, will use 5'
    )
    args = parser.parse_args()
    tsv_filename = args.train
    amount_of_intervals = args.intervals or 5
    predict_filename = args.predict
    if tsv_filename is None:
        print "Please provide tsv file"
        sys.exit(1)
    if predict_filename is None:
        print "Please provide predict file"
        sys.exit(1)

    AGE_INTERVALS, user_lists, classifier = load_training_data(
        tsv_filename, amount_of_intervals, naive_bayes.GaussianNB
    )

    print "Using age intervals: %s" % AGE_INTERVALS

    features_lists_to_predict = tsv_import.get_data_from_file(
        predict_filename, FEATURE_FIELDS, CONVERSION_FUNCTIONS)

    print FEATURE_FIELDS
    for user_features in features_lists_to_predict:
        print user_features, classifier.predict(user_features)
