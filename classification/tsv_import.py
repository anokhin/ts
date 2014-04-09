import io
from sys import argv


def get_fields(string, delimiter=u'\t'):
    """Returns a list of fields in a line, separated by delimiter"""
    fields = string.strip().split(delimiter)
    return fields


def parse_tsv(stream, delimiter=u'\t'):
    """Takes a stream
    Returns a generator of lists,
    those sublists are lists of fields for each line
    """
    for line in stream:
        yield get_fields(line, delimiter)


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

conversion_functions = {
    u'age': str_to_int_or_none,
    u'first_name': identity,
    u'friends_age': str_to_int_or_none,
    u'graduation': str_to_int_or_none,
    u'last_name': identity,
    u'school_end': str_to_int_or_none,
    u'school_start': str_to_int_or_none,
    u'uid': str_to_int_or_none
}

if __name__ == '__main__':
    with io.open(argv[1]) as tsv:
        parsed_tsv = list(parse_tsv(tsv))

        dicts = lists_to_dicts(parsed_tsv, conversion_functions)
        lists = dicts_to_lists(dicts, [
            u'age',
            u'friends_age',
            u'graduation',
            u'school_end',
            u'school_start'
        ])
        print list(lists)
