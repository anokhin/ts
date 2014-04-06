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


if __name__ == '__main__':
    with io.open(argv[1]) as tsv:
        print list(parse_tsv(tsv))
