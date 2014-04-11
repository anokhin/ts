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
        help='filename of tsv file with vk users to classify')
    parser.add_argument(
        '--train', action='store', metavar='FILE',
        help='filename of tsv file with training data'
    )
    args = parser.parse_args()
    tsv_filename = args.train
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
    AGE_INTERVALS = [(0, 16), (17, 19),
                     (20, 23), (24, 29), (30, 34), (35, 39),
                     (40, 44), (45, 49), (50, 59), (60, 99)]
    FEATURE_FIELDS = [
        u'age', u'school_start', u'school_end', u'graduation',
        u'friends_age']
    user_lists = tsv_import.get_data_from_file(tsv_filename,
                                               FEATURE_FIELDS,
                                               CONVERSION_FUNCTIONS)
    ages = tsv_import.get_ages(user_lists, FEATURE_FIELDS)

    age_intervals = tsv_import.break_on_intervals(ages, AGE_INTERVALS)

    classifier = naive_bayes.GaussianNB()
    classifier.add_classes(AGE_INTERVALS)
    classifier.fit(user_lists, age_intervals)

    features_lists_to_predict = tsv_import.get_data_from_file(
        predict_filename, FEATURE_FIELDS, CONVERSION_FUNCTIONS)

    for user_features in features_lists_to_predict:
        print user_features, classifier.predict(user_features)

    import pprint
    pprint.pprint(classifier._GaussianNB__means)
    pprint.pprint(classifier._GaussianNB__variances)
