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


if __name__ == '__main__':
    with io.open(argv[1]) as tsv:
        parsed_tsv = list(parse_tsv(tsv))
        conversion_functions = dict(zip(
            parsed_tsv[0],
            [identity] * len(parsed_tsv[0])
        ))
        dicts = lists_to_dicts(parsed_tsv, conversion_functions)
        import pprint
        pprint.pprint(dicts)
