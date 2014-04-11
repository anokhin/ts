import io
from sys import argv
import csv


def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]


def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')


def get_fields(string):
    """Returns a list of fields in a line, separated by delimiter"""
    return unicode_csv_reader([string], delimiter=',').next()


def parse_tsv(stream):
    """Takes a stream
    Returns a generator of lists,
    those sublists are lists of fields for each line
    """
    for line in stream:
        yield get_fields(line)


def lists_to_dicts(lists, conversion_functions):
    """Arguments:
        lists - a list of lists, where 1-st sublist is contains column names,
        all following sublists contain column values.
        parse_tsv function returns exactly this format.

        conversion_functions - dict like this:
            {u'field_name': converter_func1,
             u'age': converter_func2}
        Keys of this dict must contain only all values from the first sublist
        of lists. converter_func$ are functions that convert this field from
        unicode string to arbitrary type suitable for that field.

    Returns a list or dicts, each dict is like this:
        {u'age': 14,
         u'name': u'Petya',
         u'field_name': "value_generated_by_conversion_function"}
    """
    field_names = lists[0]
    if frozenset(field_names) != frozenset(list(
        conversion_functions.iterkeys()
    )):
        raise Exception('lists_to_dicts: field names from lists'
                        'and field names from conversion functions'
                        'did not match')
    converters = [conversion_functions[field] for field in field_names]
    field_values = lists[1:]
    result_dicts = [
        dict(zip(
            field_names,
            [converter(value) for converter, value in zip(converters, line)]
        ))
        for line in field_values]
    return result_dicts


def identity_or_none(x):
    if x is None or x == u'None':
        return None
    return x


def str_to_int_or_none(string):
    try:
        return int(string)
    except Exception:
        return None


def identity(x):
    return x


def dicts_to_lists(dicts, fields_order):
    """Arguments:
        dicts is a list of dicts, like the ones returned by lists_to_dicts

        fields_order is a list of text field names, like this:
            [u'age', u'graduation']

    Returns a generator of lists, where each sublist is of length
    len(fields_order) and has values of those fields in it.
    """
    for dict in dicts:
        yield [dict[field] for field in fields_order]


def extract_result_from_dicts(dicts, result_field):
    """Arguments:
        dicts is a list of dicts, like the ones returned by lists_to_dicts

        result_field is a string with name of the field we want to return

    Returns a generator with values of that result_field
    """
    for dict in dicts:
        yield dict[result_field]


def determine_intervals(amount_of_intervals, numbers):
    length = len(numbers)
    length_of_interval = length / amount_of_intervals
    sorted_numbers = sorted(numbers)
    intervals = []
    lower_limits = [
        sorted_numbers[length_of_interval * no_of_interval]
        for no_of_interval in range(amount_of_intervals)
    ]
    lower_limits = sorted(list(set(lower_limits)))
    intervals = [pair for pair in zip(
        lower_limits,
        [x - 1 for x in lower_limits][1:] + [max(100, sorted_numbers[-1])]
    )]
    return intervals


def break_on_intervals(results, intervals):
    """Arguments:
        results - list of results (ages)

        intervals - list of pairs like this:
            [(0,10), (11,20), (21,40)]
    Returns:
        list with length len(results), where each result is replaced with
        an interval to which it belongs
    """
    return [choose_interval(result, intervals) for result in results]


def choose_interval(result, intervals):
    """Arguments:
        result - number

        intervals - list of pairs like this:
            [(0,10), (11,20), (21,40)]

    Returns:
        the one interval where result belongs
    """
    for first, second in intervals:
        if first <= result <= second:
            return first, second
    raise Exception("Result didn't belong in an interval")

conversion_functions = {
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


def get_data_from_file(filename, fields, conversion_functions):
    """Arguments:
        filename - name of file to read

        fields - list of field names, ordered

        conversion functions - dict {u'field_name': conversion_function}

    Returns:
        list of sublists of features
        (each sublist is a list of features of some particular user)
    """
    with io.open(filename) as tsv_file:
        parsed_tsv = list(parse_tsv(tsv_file))
        dicts = lists_to_dicts(parsed_tsv, conversion_functions)
        user_lists = list(dicts_to_lists(dicts, fields))
        return user_lists


def get_ages(user_lists, fields):
    age_index = fields.index(u'age')
    return [features[age_index] for features in user_lists]


if __name__ == '__main__':
    with io.open(argv[1]) as tsv:
        parsed_tsv = list(parse_tsv(tsv))

        dicts = lists_to_dicts(parsed_tsv, conversion_functions)
        ages = list(extract_result_from_dicts(dicts, u'friends'))
        size = len(list(dicts[0].iterkeys()))
        from pprint import pprint
        pprint(dicts[:30])
