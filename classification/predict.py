import argparse
import sys

import tsv_import
import naive_bayes

from tsv_import import str_to_int_or_none
from tsv_import import identity

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

    CONVERSION_FUNCTIONS = {
        u'age': str_to_int_or_none,
        u'first_name': identity,
        u'friends_age': str_to_int_or_none,
        u'graduation': str_to_int_or_none,
        u'last_name': identity,
        u'school_end': str_to_int_or_none,
        u'school_start': str_to_int_or_none,
        u'uid': str_to_int_or_none
    }
    FEATURE_FIELDS = [
        u'age', u'school_start', u'school_end', u'graduation',
        u'friends_age']
    user_lists = tsv_import.get_data_from_file(tsv_filename,
                                               FEATURE_FIELDS,
                                               CONVERSION_FUNCTIONS)
    ages = tsv_import.get_ages(user_lists, FEATURE_FIELDS)
    AGE_INTERVALS = tsv_import.determine_intervals(
        amount_of_intervals, ages)
    print "Using age intervals: %s" % AGE_INTERVALS

    age_classes = tsv_import.break_on_intervals(ages, AGE_INTERVALS)

    classifier = naive_bayes.GaussianNB()
    classifier.fit(user_lists, age_classes)

    features_lists_to_predict = tsv_import.get_data_from_file(
        predict_filename, FEATURE_FIELDS, CONVERSION_FUNCTIONS)

    print FEATURE_FIELDS
    for user_features in features_lists_to_predict:
        print user_features, classifier.predict(user_features)

    #import pprint
    #pprint.pprint(classifier._GaussianNB__means)
    #pprint.pprint(classifier._GaussianNB__variances)
