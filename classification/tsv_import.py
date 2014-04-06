import io


def get_fields(string, delimiter=u'\t'):
    """Returns a list of fields in a line, separated by delimiter"""
    fields = string.strip().split(delimiter)
    return fields
